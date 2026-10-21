# Score donation descriptions

The score-only basket posts a voluntary General Fund contribution using the existing PayPal Payments Standard `_donations` form. Downloads, recipient, GBP currency, editable suggested amount and payment method are unchanged. The CD order service and general donation page are separate and unchanged.

## Transaction fields

- `item_name` (127 characters): `Hans Gál Society — General Fund — Scores: ` followed by selected work titles and opus numbers. Titles come from the active language's catalogue. HTML markup/entities become plain text. If necessary, titles are shortened while retaining opus numbers; works without an opus retain `[#id]` when abbreviated. If titles still cannot fit, the description uses opus numbers or `#id` alone.
- `custom` (255 characters): `Scores: ` followed by the fuller itemised selection, using the same abbreviation rules only if necessary. All currently downloadable scores together fit with full titles in this field in each published language.
- `item_number` (127 characters): compact opus numbers, or `#id` for a work without an opus number. `#149`, for example, identifies catalogue work `/works/show/149/`. These are public work references, not visitor identifiers.

Each field independently fits its limit. Unicode code points are counted and surrogate pairs are never split. An exceptionally large selection that cannot fit even as numeric references ends with `+N more`; no static Donate field can hold an unlimited selection. This also applies to `custom`: a complete title list is possible only within its own limit. No names, visitor identifiers, timestamps or download tracking are added.

## PayPal documentation checked 21 October 2026

- [HTML variables for PayPal Payments Standard](https://developer.paypal.com/api/nvp-soap/paypal-payments-standard/integration-guide/Appx-websitestandard-htmlvariables/?mark=handling_cart): `item_name` and `item_number` support contributions and have 127-character limits. The generic HTML table lists `custom` as 256 characters; the IPN/PDT documentation limits its returned value to 255, so this implementation uses 255. Option fields `on0`/`os0` and related fields explicitly do **not** support Donate buttons.
- [IPN and PDT variables](https://developer.paypal.com/api/nvp-soap/ipn/IPNandPDTVariables): describes `item_name`, `item_number` and `custom` returned with transaction information, including Donate (`web_accept`) transactions. IPN is a machine notification, not the Society's payment email. This change does not install or require an IPN receiver.
- [Donate SDK](https://developer.paypal.com/sdk/donate): confirms Donate button support for `item_name` and `item_number`; no SDK migration is needed.

The principal identification is in the actual PayPal transaction description, not merely browser text. It replaces the same `item_name` that previously generated the generic score-availability notification. That makes titles available as the payment description and should place them in the Society's usual notification, subject to PayPal's email template. No guarantee is made about email layout, whether `custom` appears in the account UI/email, or every account's presentation of additional fields. The documentation's explicit `custom` email promise is in the **subscription** section; it is not treated as a Donate email guarantee.

No payment was initiated and no PayPal account was accessed. Tests verify the real basket's generated outgoing form fields and submit validation with mocked DOM/storage/catalogue fetches; they do not prove PayPal's processing or the delivered merchant email. A future legitimate contribution or a separately authorised PayPal sandbox transaction can confirm the recipient-side presentation. Past transactions cannot acquire these new fields retroactively.

## Regression check

`node tests/donations.test.cjs` includes `tests/score-donations.test.cjs`, so the existing Pages workflow runs the new coverage. Build first with `python scripts/build.py --base-path /hansgal-org`. Coverage includes single/multiple works, current full selections in all four languages, lengthy titles, number-only fallback, large baskets, Unicode and HTML entities, edited/remembered amounts, zero/invalid amounts, duplicates and empty/unknown selections. No payment requests are made.
