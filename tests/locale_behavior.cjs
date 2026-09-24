// Exercise the generated controller as a visitor moving between static pages.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const script = fs.readFileSync('assets/locale.js', 'utf8');
const locales = ['en', 'de', 'es', 'es-419', 'fr', 'hi', 'ja', 'ko', 'pt', 'pt-BR', 'zh', 'zh-Hant'];
const memory = new Map();

function makePage(url, browserLanguages) {
  const sections = locales.map(locale => ({
    dataset: {locale}, hidden: false,
    querySelector(selector) {
      if (selector === 'h1') return {textContent: `Title ${locale}`};
      if (selector === '.lede') return {textContent: `Summary ${locale}`};
      return null;
    },
  }));
  const choices = locales.map(locale => ({
    dataset: {choose: locale}, attributes: {}, handlers: {},
    setAttribute(key, value) { this.attributes[key] = value; },
    removeAttribute(key) { delete this.attributes[key]; },
    addEventListener(type, handler) { this.handlers[type] = handler; },
  }));
  const makeLink = (href, navIndex) => ({
    dataset: navIndex === undefined ? {} : {nav: String(navIndex)},
    href, textContent: '', getAttribute() { return this.href; },
  });
  const nav = [0, 1, 2, 3].map(index => makeLink(`../page-${index}/`, index));
  const brand = makeLink('../');
  const card = makeLink('../privacy/');
  const updated = {textContent: ''};
  const meta = {content: ''};
  const languageSwitch = {attributes: {}, setAttribute(key, value) { this.attributes[key] = value; }};
  const document = {
    documentElement: {lang: '', classList: {add() {}}}, title: '',
    querySelectorAll(selector) {
      return {
        '.locale-section': sections,
        '.locale-choice': choices,
        '[data-nav]': nav,
        '[data-updated]': [updated],
        'a[data-nav], a.brand, a.card': [...nav, brand, card],
      }[selector] || [];
    },
    querySelector(selector) {
      if (selector === '.locale-section:not([hidden])') return sections.find(section => !section.hidden);
      if (selector === 'meta[name="description"]') return meta;
      if (selector === '[data-language-switch]') return languageSwitch;
      return null;
    },
  };
  const location = new URL(url);
  let changedUrl;
  const context = {
    URL, URLSearchParams, document, location,
    navigator: {languages: browserLanguages},
    localStorage: {
      getItem(key) { return memory.get(key) || null; },
      setItem(key, value) { memory.set(key, value); },
    },
    history: {replaceState(_state, _unused, value) { changedUrl = String(value); }},
    window: {scrollTo() {}},
  };
  vm.runInNewContext(script, context, {filename: 'assets/locale.js'});
  return {sections, choices, nav, document, meta, languageSwitch, get changedUrl() { return changedUrl; }};
}

const first = makePage('https://example.com/yido-legal/?lang=de', ['en-US']);
assert.equal(first.document.documentElement.lang, 'de');
assert.equal(first.sections.filter(section => !section.hidden)[0].dataset.locale, 'de');
assert.equal(first.sections.filter(section => section.hidden).length, 11);
assert.equal(first.nav[0].textContent, 'Datenschutz');
assert.equal(first.languageSwitch.attributes['aria-label'], 'Sprache');
assert.equal(first.document.title, 'Title de · Yido');

first.choices.find(choice => choice.dataset.choose === 'zh-Hant').handlers.click({preventDefault() {}});
assert.equal(first.document.documentElement.lang, 'zh-Hant');
assert.equal(first.nav[0].textContent, '隱私權政策');
assert.equal(first.languageSwitch.attributes['aria-label'], '語言');
assert.match(first.nav[0].href, /lang=zh-Hant/);
assert.match(first.changedUrl, /lang=zh-Hant/);
assert.equal(memory.get('yido-legal-locale'), 'zh-Hant');

const nextPage = makePage('https://example.com/yido-legal/privacy/', ['en-US']);
assert.equal(nextPage.document.documentElement.lang, 'zh-Hant');
assert.equal(nextPage.sections.find(section => !section.hidden).dataset.locale, 'zh-Hant');

const queryWins = makePage('https://example.com/yido-legal/support/?lang=pt-BR', ['de-DE']);
assert.equal(queryWins.document.documentElement.lang, 'pt-BR');
assert.equal(queryWins.nav[3].textContent, 'Ajuda');

memory.clear();
assert.equal(makePage('https://example.com/yido-legal/privacy/', ['zh-TW']).document.documentElement.lang, 'zh-Hant');
assert.equal(makePage('https://example.com/yido-legal/privacy/', ['es-MX']).document.documentElement.lang, 'es-419');
assert.equal(makePage('https://example.com/yido-legal/privacy/', ['xx-XX']).document.documentElement.lang, 'en');

console.log('Locale selection, switching, and cross-page persistence passed.');
