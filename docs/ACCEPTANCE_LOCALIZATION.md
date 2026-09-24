# Legal site localization acceptance

- [ ] On each of the five public URLs, a visitor can choose every locale supported by the Yido app: `en`, `de`, `es`, `es-419`, `fr`, `hi`, `ja`, `ko`, `pt`, `pt-BR`, `zh`, `zh-Hant`.
- [ ] Choosing a locale changes the page body, navigation, page title, and footer together. The choice carries to the other legal pages; an unsupported browser locale falls back to English. Content remains readable when JavaScript is unavailable.
- [ ] Every locale gives the same material disclosures about on-device data, OS backup and deliberate sharing, optional permissions, store purchases, parent controls, operator identity, and a private contact route for children's data requests.
- [ ] Existing paths stay stable: `/`, `/privacy/`, `/terms/`, `/children-privacy/`, `/support/`.
- [ ] All five pages and 12 locales have complete content and working internal links. Every support request has a usable private email route; no link sends users to the private code repository's issue tracker.

Verification: run the repository's localization regression test, review one mobile and one desktop viewport, and manually spot-check meaning across each locale. Final legal and native-speaker acceptance belongs to the publisher; automated checks do not approve it.

Implementation evidence (2026-09-25): six Python regression cases pass; the generated JavaScript passes syntax validation and a Node visitor-flow case for locale choice, cross-page persistence, and browser fallback. Local browser inspection covered German desktop and Traditional Chinese page-to-page navigation; at 390 px viewport width the support page had no horizontal overflow. The GitHub Pages artifact contains only the five public pages and assets. Mailbox receipt, live Pages deployment, native-speaker review, and publisher legal acceptance remain to be confirmed.
