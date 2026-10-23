# Bank transfer details requests

The static GitHub Pages website uses the existing Hans Gál Society orders service for email delivery. The public configuration contains only its `/api/bank-details` URL. Bank instructions and complete approved EN/DE/FR/JA email bodies are private runtime secrets on that service, outside this repository and all website build files. No new provider account, DNS change, or mail credential is needed.

The Society information, Donate, Membership and Live Performance Fund pages use the same compact email form as the score basket. Existing PayPal, cheque and free score-download behaviour is retained. CD checkout explains that banking instructions arrive in the existing order-confirmation email. It no longer includes bank account data in the shared language bundle or the public order API response.

Requests send only an email address, language, fixed fund key, signed challenge/proof and empty honeypot. The recipient cannot supply email text or links. No address is saved in browser storage. The service uses a signed, IP-bound, ten-minute automatic proof-of-work challenge and atomic database limits: three new emails per IP/hour, ten per IP/day, one per normalised email per rolling 24 hours, and forty bank-request emails/day UTC. Limits are independent of existing order/contact quotas. IP and address values become keyed hashes before rate-limit storage. Request records expire after 24 hours and are deleted on the next request. Resend and the recipient mailbox process the email itself; the form links the processors' privacy policies. Proof of work increases automation cost; it does not prove a visitor is human.

## Validation and rollout

1. Backend: run `node tests/bank-details.cjs`, `node tests/orders.cjs`, `node tests/contact.cjs` and the Sites production build in the private order-service source. Deploy the tested service and required D1 migration first. Its `BANK_REQUESTS_ENABLED` switch and runtime secrets must be configured.
2. Public source: run the existing repository checks, `node tests/bank-details.test.cjs` and `node tests/bank-form.test.cjs`. The first new check scans generated pages, JSON and browser assets for bank account exposure; the second tests form success/failure, retry identity, four languages and dynamic remounting without sending messages.
3. Perform an explicitly authorised real delivery test, read the received message and check its exact content, and verify an identical retry does not send again. Then exercise the actual production-origin browser form. Do not merge or remove the existing live bank instructions before this gate passes.
4. Merge the reviewed public changes, wait for GitHub Pages, and verify the actual hosted Society and basket pages in English/German (and retained additional languages). The exact current public source is covered by the normal editorial field hashes; preservation fingerprints and legacy fixtures are unchanged.

A disabled/misconfigured service fails closed. The form shows a delivery failure and a Society contact link; it does not reveal bank details. To suspend requests, set `BANK_REQUESTS_ENABLED=false` through Sites runtime settings and redeploy. Restore the switch and redeploy to resume. Keep approved email/body edits in private runtime secrets; never paste their values into issues, documentation, test fixtures or commit messages.

Removing bank details from the current source and build cannot erase already-public Git history, caches or downloaded copies. This workflow reduces casual discovery and bulk collection; it cannot make previously published account information secret.

## Current acceptance state

Backend version 4 is deployed. Its live anonymous challenge endpoint responds correctly. Mocked delivery/security tests and the existing order/contact tests pass. The public build and integrity checks pass, and the Society form/language switch and failure recovery were inspected in the internal browser preview. No real bank-request email has been sent: the final delivery test requires an explicitly authorised recipient. Public changes must remain unmerged until that test is complete.
