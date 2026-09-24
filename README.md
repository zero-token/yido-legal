# Yido Legal & Support

Public legal and support pages for Yido, published with GitHub Pages. All five
pages support the 12 language/region variants used by the app: `en`, `de`, `es`,
`es-419`, `fr`, `hi`, `ja`, `ko`, `pt`, `pt-BR`, `zh`, and `zh-Hant`.

- `/privacy/`
- `/terms/`
- `/children-privacy/`
- `/support/`

These pages describe the current `kids` distribution channel. Review them whenever Yido's data handling, SDKs, purchases, or support contact changes.

Edit `content/existing.json`, `content/additional.py`, or `content/site_text.py`,
then rebuild and test:

```sh
python3 tool/build_site.py
python3 -m unittest discover -s tests -v
node --check assets/locale.js
node tests/locale_behavior.cjs
```

The generated HTML is checked in so visitors can read all translations when
JavaScript is disabled. With JavaScript, the browser language is selected by
default and an explicit choice follows the visitor between pages. Product,
privacy, and children's data requests all use the private support email.
