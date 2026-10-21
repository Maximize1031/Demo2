# Intake assessment

Case: Rivera Orchard LLC
Case ID: DEMO-RIVERA-001
Property: 1250 Orchard Avenue, Pasadena, CA 91103
Mode: Synthetic post-ingestion workflow rehearsal
Revision: initial
Source records: 5

| ID | Item | State | Owner | Value | Evidence |
| --- | --- | --- | --- | --- | --- |
| entity | Entity type | found | client | Single-member LLC | 01-client-brief.md §Owner and contact: “a single-member LLC” |
| titleholder | Name on title | found | escrow | Rivera Orchard LLC | 04-preliminary-title.md §Ownership and property: “Name on title: Rivera Orchard LLC” |
| taxpayer | Taxpayer name | found | client | Maya Rivera — client reported | 01-client-brief.md §Owner and contact: taxpayer name is Maya Rivera |
| tax-id | Tax ID secure receipt | missing | client | Arrange secure delivery; never email the number | 01-client-brief.md §Owner and contact: “has not been received through a secure channel” |
| mailing | Owner mailing address | found | client | 410 Example Lane, Pasadena, CA 91101 | 01-client-brief.md §Owner and contact: owner mailing address |
| owner-phone | Owner phone | found | client | (626) 555-0142 | 01-client-brief.md §Owner and contact: owner and primary contact phone |
| contact-name | Primary contact name | found | client | Maya Rivera | 01-client-brief.md §Owner and contact: primary contact |
| contact-email | Primary contact email | found | client | maya.rivera@example.com | 01-client-brief.md §Owner and contact: primary contact email |
| contact-phone | Primary contact phone | found | client | (626) 555-0142 | 01-client-brief.md §Owner and contact: owner and primary contact phone |
| authority | Who can sign | review | client | Confirm whether Maya can sign for the LLC | 01-client-brief.md §Owner and contact: signing authority unconfirmed; 05-call-notes.md §Notes: call did not establish signer |
| other-signer | Other signer details | review | client | Only needed if Maya cannot sign; ask conditionally in the same question | 01-client-brief.md §Owner and contact: signing authority has not been confirmed |
| property | Property being sold | found | escrow | 1250 Orchard Avenue, Pasadena, CA 91103 | 04-preliminary-title.md §Ownership and property; 02-sale-agreement.md §Parties and property |
| closing | Estimated closing date | conflict | escrow | November 6 vs November 9, 2026 — confirm with escrow | 02-sale-agreement.md §Closing: “November 6, 2026”; 03-email-thread.md §Message 2: “November 9” |
| contract | Sale agreement | found | escrow | Synthetic document on file; no need to resend | 02-sale-agreement.md §Document receipt: matching PDF present, synthetic signed fixture |
| title | Preliminary title report | found | escrow | Synthetic document on file; no need to resend | 04-preliminary-title.md §Document receipt: matching PDF present |
| escrow-name | Escrow contact | found | escrow | Elena Park | 03-email-thread.md §Message 2: sender Elena Park |
| escrow-email | Escrow email | found | escrow | elena.park@example.com | 03-email-thread.md §Message 2: sender email |
| escrow-phone | Escrow phone | found | escrow | (626) 555-0168 | 03-email-thread.md §Message 2: escrow officer signature details |
| escrow-company | Escrow company | found | escrow | Harbor Example Escrow | 03-email-thread.md §Message 2: “Harbor Example Escrow” |
| entity-doc | LLC operating agreement | missing | client | Request the agreement once | 03-email-thread.md §Message 2: “I do not have the LLC operating agreement yet”; 05-call-notes.md §Notes: Maya will locate it |
| interest | Interest shared with owner | found | internal | No | 01-client-brief.md §Transaction and internal context: interest will not be shared |
| w9 | W-9 | not_applicable | client | Not required in this scenario because interest is not shared | 01-client-brief.md §Transaction and internal context: interest will not be shared |
| referral | Internal referral | found | internal | Jordan Ellis; jordan.ellis@example.com; (626) 555-0199 | 01-client-brief.md §Transaction and internal context: internal referral contact |
| admin | Accruit admin assignment | missing | internal | Shant to request assignment | 01-client-brief.md §Transaction and internal context: assignment has not yet been requested |
| notes | Special terms | found | internal | No unusual terms reported | 01-client-brief.md §Transaction and internal context: no seller financing, back-to-back or unusual fees reported |
| replacement | Replacement property | optional | client | Not yet identified; not blocking intake | 01-client-brief.md §Transaction and internal context; 05-call-notes.md §Notes |
| price | Sale price | found | escrow | $2,450,000 | 02-sale-agreement.md §Parties and property: sale price |
| loan | Existing loan balance | optional | client | Not in reviewed records; no request at this stage | 04-preliminary-title.md §Document receipt: no loan balance provided; reviewed all five initial Markdown sources |

## Change log

October 15, 2026: Read the five initial source records. Kept the two closing dates unresolved. Authority and conditional other-signer details require review. Request only missing owner information and closing-date confirmation.

## Review status

Prepared from synthetic Markdown records. Document receipt is synthetic. No live connectors, actual client records, email delivery, or Accruit submission. The expected close is not an actual transfer date. Checklist completeness is not professional approval.
