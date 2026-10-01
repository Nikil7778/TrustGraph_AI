# TrustGraph AI

TrustGraph AI analyzes recruitment notices and presents evidence that may indicate fraud. The frontend sends an analysis request to the backend, which runs it through this pipeline:

1. **Process input** - normalize the submitted notice into text and metadata.
2. **Extract evidence** - identify recruitment details such as organization, contacts, fees, and links.
3. **Generate Recruitment DNA** - organize the extracted details into a comparable record.
4. **Build evidence graph** - connect related details to show how the evidence fits together.
5. **Verify official details** - compare the notice with the official registry.
6. **Match suspicious fingerprints** - compare its details with known suspicious records.
7. **Reason about risk** - summarize the verification and matching evidence.
8. **Calculate trust score** - combine the evidence into a score and risk level.
9. **Compose result** - save the analysis and return an explainable dashboard with findings and recommended actions.

The dashboard presents the stages and final result so users can inspect the evidence behind the risk assessment.