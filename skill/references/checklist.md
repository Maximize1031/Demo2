# Intake checklist

Derived from the supplied v1 skill and its Exchange Manager Pro field reference. Not independently verified against the current Accruit interface. Groups such as address and referral contact are complete only when every listed component is supported.

| ID | Item | Owner | Requirement |
| --- | --- | --- | --- |
| entity | Entity type | client | required |
| titleholder | Name on title | escrow | required |
| taxpayer | Taxpayer name | client | required |
| tax-id | Tax ID receipt confirmation only | client | required |
| mailing | Owner mailing address, city, state, ZIP | client | required |
| owner-phone | Owner phone | client | required |
| contact-name | Primary contact name | client | required |
| contact-email | Primary contact email | client | required |
| contact-phone | Primary contact phone | client | required |
| authority | Primary contact authorized to sign? | client | required |
| other-signer | Other signer name, email, phone | client | conditional: primary contact is not signer |
| property | Sale property address, city, state, ZIP | escrow | required |
| closing | Closing date and estimated/actual status | escrow | required |
| contract | Sale purchase agreement received | escrow | required |
| title | Preliminary title report received | escrow | required |
| escrow-name | Closing agent name | escrow | required |
| escrow-email | Closing agent email | escrow | required |
| escrow-phone | Closing agent phone | escrow | required |
| escrow-company | Closing agent company | escrow | required |
| entity-doc | Entity-specific document received | client | conditional: entity is not individual |
| interest | Whether interest is shared with taxpayer | internal | required to determine W-9 applicability |
| w9 | W-9 receipt confirmation only | client | conditional: interest shared |
| referral | Internal referral name, email, phone | internal | required; phone is conservatively retained from detailed source table |
| admin | Accruit administrator assignment requested | internal | internal follow-up |
| notes | Special terms or explicit none | internal | internal follow-up |
| replacement | Replacement address, price, estimated close, available agreement/title | client | optional at intake |
| price | Sale price | escrow | optional |
| loan | Existing loan amount | client | optional |

## Conditions

- Individual: entity document is not applicable. Single- or multi-member LLC: operating agreement. Corporation: corporate signing resolution. Trust: trust documents. Partnership: partnership agreement. Unknown entity: entity and entity document require review.
- Primary contact confirmed as signer: other signer is not applicable. Confirmed not signer: require all other signer details. Unknown authority: authority and other signer require review.
- Interest shared: W-9 required. Confirmed no: not applicable. Unknown: interest and W-9 require review. Store only secure receipt status; never the form contents or tax ID.
- Replacement plans and loan amount do not block intake. Do not request them merely to fill an optional blank.
- Internal admin tasks are visible but excluded from client and escrow emails.
- Duplicate content is one piece of evidence, not multiple confirmations. A receipt claim without the underlying document can support “receipt reported”; distinguish this from content reviewed. In this demo, paired synthetic PDF + Markdown records support synthetic receipt, never real receipt.
- A known email address does not establish signing authority. A property address does not establish an owner mailing address. A titleholder name does not establish the taxpayer name.

## States

`found`: supported fact/receipt, no unresolved contradiction. `missing`: absent from the reviewed input set. `conflict`: contradictory evidence. `review`: incomplete, uncertain, or conditional applicability unresolved. `not_applicable`: condition explicitly false. `optional`: absent nonblocking information.

The UI counts rows, not raw fields. Label counts “checklist items.” Do not label the case ready for submission solely because all rows are found; professional review and live vendor requirements remain separate.
