# Reference Document Reconstruction

This file reconstructs the provided reference images into normalized markdown data.

## Source Set

- Dashboard odometer/trip display image
- North Carolina driver license (front) image
- North Carolina registration card image
- Vehicle manufacturer VIN/weight label image

## Person (from Driver License)

| Field | Value |
| --- | --- |
| Full name | TODD ALLEN HINTZMANN |
| Address line 1 | 1104 E 35TH ST |
| City | CHARLOTTE |
| State | NC |
| ZIP | 28205-1615 |
| Date of birth | 04/27/1973 |
| License state | NC |
| License number | 00021666224 |
| Class | C |
| Restrictions | 1 |
| Sex | M |
| Height | 5-09 |
| Weight (lb) | 160 |
| Eyes | BLU |
| Hair | BAL |
| Issue date | 05/23/2024 |
| Expiration date | 04/27/2032 |

## Vehicle (from Registration + VIN Label)

| Field | Value |
| --- | --- |
| VIN | 1F64F5DY4D0A12593 |
| Year | 2014 |
| Make | THOR |
| Plate number | 04M8SM |
| Style | HC |
| Fuel | G |
| GVWR | 7258 kg (16000 lb) |
| Front GAWR | 2948 kg (6500 lb) |
| Rear GAWR | 4990 kg (11000 lb) |
| Tire spec | 245/70R19.5G 133/132L |
| Rim spec | 19.5x6.75 |
| Tire pressure (cold) | 565 kPa / 82 PSI |

## Registration (from NC Registration Card)

| Field | Value |
| --- | --- |
| State | NC |
| Plate number | 04M8SM |
| Plate expiration | 08/31/2025 |
| Inspection due | 08/31/2025 |
| VIN | 1F64F5DY4D0A12593 |
| Year | 2014 |
| Make | THOR |
| Style | HC |
| Fuel | G |
| Total fee | 587.23 |
| County | MECKL |
| Classification | GREAT SMOKY MOUNTAINS PAS |
| Policy number | 2012607039 |
| Insurance company | NATIONAL GENERAL INSURANCE CO |
| Insurance authorized in NC | Yes |

## Odometer Snapshot (from Dashboard)

| Field | Value |
| --- | --- |
| Odometer | 42575 mi |
| Trip | 14.1 |

## Normalized JSON Seed Alignment

The values above are the source used for the onboarding seed in:
- `_bmad-output/lens-work/personal/reference-seed.json` (written by onboard.py)
- `REFERENCE_SEED` constant in `onboard.py`

## Data Quality Notes

- Values are reconstructed from images and normalized for consistency.
- Date formats in this markdown preserve the card display style where shown.
- The onboarding seed uses ISO dates where practical (for machine-friendly processing).
