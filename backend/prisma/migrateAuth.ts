import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { randomBytes } from 'crypto';

const prisma = new PrismaClient();

function normalize(value: string): string {
  return value.trim().toLocaleLowerCase('en-US');
}

function makeUsername(value: string): string {
  return value.replace(/[^a-zA-Z0-9_]/g, '').slice(0, 24) || 'user';
}

async function main() {
  const users = await prisma.user.findMany({ orderBy: { createdAt: 'asc' } });
  const used = new Set(
    users.filter(user => user.usernameNormalized).map(user => user.usernameNormalized as string)
  );

  for (const user of users) {
    if (user.username && user.usernameNormalized && user.passwordHash) continue;

    const isAdmin = user.role === 'ADMIN';
    const base = isAdmin ? 'admin' : makeUsername(user.email?.split('@')[0] || user.name || `user_${user.id.slice(0, 6)}`);
    let username = user.username || base;
    let usernameNormalized = normalize(username);

    if ((!isAdmin && usernameNormalized === 'admin') || (used.has(usernameNormalized) && usernameNormalized !== user.usernameNormalized)) {
      const suffix = user.id.replace(/-/g, '').slice(0, 6).toLowerCase();
      username = `${base.slice(0, 17)}_${suffix}`;
      usernameNormalized = normalize(username);
    }
    used.add(usernameNormalized);

    let passwordHash = user.passwordHash;
    if (!passwordHash && user.password) {
      try {
        bcrypt.getRounds(user.password);
        passwordHash = user.password;
      } catch {
        passwordHash = await bcrypt.hash(user.password, 12);
      }
    }
    if (!passwordHash) passwordHash = await bcrypt.hash(randomBytes(32).toString('hex'), 12);

    await prisma.user.update({
      where: { id: user.id },
      data: {
        username,
        usernameNormalized,
        passwordHash,
        password: null,
        role: isAdmin ? 'ADMIN' : 'USER'
      }
    });
  }

  console.log(`Migrated ${users.length} existing user account(s).`);
}

main()
  .catch(() => {
    console.error('Account migration failed. No account credentials were logged.');
    process.exitCode = 1;
  })
  .finally(async () => prisma.$disconnect());