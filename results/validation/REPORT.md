# Figure 1 validation

Across 175 sample–gene observations from 72 cell lines, the table below compares two ways of applying the neutral-case rule. TP and FN use double minutes (DM) on metaphase FISH as evidence of ecDNA. Precision is TP/(TP+FP) and recall is TP/(TP+FN).

| Scoring policy | TP | FP | TN | FN | Neutral | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Literal Methods rule | 53 | 9 | 81 | 3 | 29 | 85.5% | 94.6% |
| Rule consistent with Figure 1d | 53 | 5 | 81 | 3 | 33 | 91.4% | 94.6% |

Both calculations first exclude three indeterminate FISH results, then six additional unknown AC calls. One of the three indeterminate FISH observations also has an unknown AC call. The Methods specify that an ecDNA call paired with a non-native homogeneously staining region (HSR) is neutral because integration is possible. Supplementary Table 2 contains 20 such observations. Four more ecDNA calls have unknown HSR location because a centromere was unprobed. Treating these four as false positives follows the literal rule. Treating them as neutral yields all four Figure 1d counts and both Figure 1e percentages. This second treatment is inferred from agreement with the figure. The records do not establish integration in those four cases.

The program reads the FISH_results sheet in [Supplementary Table 2](https://pmc-oa-opendata.s3.amazonaws.com/PMC13736199.1/41592_2026_3264_MOESM4_ESM.xlsx), scores each row independently, and checks the rounded percentages against the Figure1e sheet in the [source data](https://pmc-oa-opendata.s3.amazonaws.com/PMC13736199.1/41592_2026_3264_MOESM11_ESM.xlsx). The count reference comes from [Figure 1d](https://pmc.ncbi.nlm.nih.gov/articles/PMC13736199/#Fig1). No genome coordinates enter this calculation. It evaluates the authors’ deposited calls against their deposited imaging labels.
