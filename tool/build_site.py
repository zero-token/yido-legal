#!/usr/bin/env python3
"""Build static, readable legal pages from reviewed locale content."""

from html import escape
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "content"))
from additional import ADDITIONAL  # noqa: E402
from site_text import ORDER, UI  # noqa: E402

EXISTING = json.loads((ROOT / "content" / "existing.json").read_text(encoding="utf-8"))
PAGES = (("", "home", -1), ("privacy", "privacy", 0), ("terms", "terms", 1),
         ("children-privacy", "children", 2), ("support", "support", 3))
EMAIL = "welcome.yido@foxmail.com"


def e(value):
    return escape(value, quote=True)


def body_for(locale, page):
    t = UI[locale]
    if page == "home":
        cards = "".join(
            f'<a class="card" href="{slug}/"><strong>{e(t["nav"][i])}</strong>'
            f'<span>{e(t["cards"][i])}</span></a>'
            for i, slug in enumerate(("privacy", "terms", "children-privacy", "support"))
        )
        return f'<h1>{e(t["home_title"])}</h1><p class="lede">{e(t["home_lead"])}</p><div class="cards">{cards}</div>'
    if page == "support":
        return (f'<h1>{e(t["nav"][3])}</h1><p class="lede">{e(t["support_intro"])}</p>'
                f'<h2>{e(t["support_private"])}</h2><div class="callout"><a href="mailto:{EMAIL}">{EMAIL}</a></div>'
                f'<h2>{e(t["support_public"])}</h2><p>{e(t["support_tips"])}</p>'
                f'<h2>{e(t["support_data_heading"])}</h2><p>{e(t["support_data"])}</p>'
                f'<h2>{e(t["support_store_heading"])}</h2><p>{e(t["support_store"])}</p>')
    if locale in EXISTING:
        body = EXISTING[locale][page]
    else:
        body = ADDITIONAL[locale][page]
    if page == "terms":
        body += f'<div class="callout">{e(t["trial_notice"])}</div>'
    return body


def contact_panel(locale):
    t = UI[locale]
    address = {
        "zh": "中国上海市闵行区 / Minhang District, Shanghai, China",
        "zh-Hant": "中國上海市閔行區 / Minhang District, Shanghai, China",
    }.get(locale, "Minhang District, Shanghai, China / 中国上海市闵行区")
    return (f'<aside class="contact-panel"><h2>{e(t["contact_heading"])}</h2>'
            f'<p><strong>{e(t["operator"])}:</strong> 王正仲 / Wang Zhengzhong<br>'
            f'<strong>{e(t["address"])}:</strong> {e(address)}<br>'
            f'<strong>{e(t["contact"])}:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p></aside>')


def render(slug, page, nav_index):
    prefix = "" if not slug else "../"
    sections = []
    for locale in ORDER:
        t = UI[locale]
        content = body_for(locale, page)
        sections.append(
            f'<section class="locale-section" id="locale-{e(locale)}" data-locale="{e(locale)}" lang="{e(t["lang"])}">'
            f'<p class="meta">{e(t["updated"])}</p>{content}{contact_panel(locale)}</section>'
        )
    choices = "".join(
        f'<a class="locale-choice" href="?lang={e(locale)}#locale-{e(locale)}" data-choose="{e(locale)}" '
        f'lang="{e(UI[locale]["lang"])}">{e(UI[locale]["label"])}</a>'
        for locale in ORDER
    )
    nav = "".join(
        f'<a data-nav="{i}" href="{prefix}{path}/">{e(UI["en"]["nav"][i])}</a>'
        for i, path in enumerate(("privacy", "terms", "children-privacy", "support"))
    )
    title = "Yido · Legal & Support" if page == "home" else f'{UI["en"]["nav"][nav_index]} · Yido'
    description = UI["en"]["home_lead"] if page == "home" else f'{UI["en"]["nav"][nav_index]} for Yido Kids.'
    html = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><meta name="description" content="{e(description)}">'
            f'<link rel="stylesheet" href="{prefix}assets/style.css">'
            f'<script defer src="{prefix}assets/locale.js"></script></head>\n<body>'
            f'<header><div class="shell"><a class="brand" href="{prefix}"><span class="mark">Y</span>Yido</a>'
            f'<nav aria-label="Yido">{nav}</nav></div></header>\n'
            f'<main class="shell"><div class="lang-switch" role="navigation" data-language-switch aria-label="Language">{choices}</div>'
            + "\n".join(sections) + '</main>\n'
            f'<footer><div class="shell">© 2026 Yido · <span data-updated>{e(UI["en"]["updated"])}</span></div></footer>'
            '</body></html>\n')
    output = ROOT / slug / "index.html"
    output.write_text(html, encoding="utf-8")


def build_script():
    public_ui = {locale: {"lang": t["lang"], "nav": t["nav"], "updated": t["updated"],
                          "languageLabel": t["language_label"]}
                 for locale, t in UI.items()}
    js = "const ui = " + json.dumps(public_ui, ensure_ascii=False, separators=(",", ":")) + ";\n"
    js += r'''
const supported = Object.keys(ui);
const params = new URLSearchParams(location.search);
function normalize(value) {
  if (!value) return null;
  const raw = value.replace('_', '-');
  const exact = supported.find(code => code.toLowerCase() === raw.toLowerCase());
  if (exact) return exact;
  if (/^zh-(TW|HK|MO|Hant)/i.test(raw)) return 'zh-Hant';
  if (/^zh/i.test(raw)) return 'zh';
  if (/^es-(?!ES)(?:[A-Z]{2}|419)$/i.test(raw)) return 'es-419';
  if (/^es/i.test(raw)) return 'es';
  if (/^pt-BR/i.test(raw)) return 'pt-BR';
  if (/^pt/i.test(raw)) return 'pt';
  const base = raw.split('-')[0].toLowerCase();
  return supported.includes(base) ? base : null;
}
function storedLocale() {
  try { return localStorage.getItem('yido-legal-locale'); } catch (_) { return null; }
}
function remember(locale) {
  try { localStorage.setItem('yido-legal-locale', locale); } catch (_) { /* private mode */ }
}
function chooseInitial() {
  const query = normalize(params.get('lang'));
  if (query) return query;
  const saved = normalize(storedLocale());
  if (saved) return saved;
  for (const preference of (navigator.languages || [navigator.language])) {
    const match = normalize(preference);
    if (match) return match;
  }
  return 'en';
}
function activate(locale, updateUrl = false) {
  const config = ui[locale] || ui.en;
  document.documentElement.lang = config.lang;
  document.documentElement.classList.add('has-locale');
  for (const section of document.querySelectorAll('.locale-section')) {
    section.hidden = section.dataset.locale !== locale;
  }
  for (const choice of document.querySelectorAll('.locale-choice')) {
    if (choice.dataset.choose === locale) choice.setAttribute('aria-current', 'true');
    else choice.removeAttribute('aria-current');
  }
  for (const link of document.querySelectorAll('[data-nav]')) {
    link.textContent = config.nav[Number(link.dataset.nav)];
  }
  const languageSwitch = document.querySelector('[data-language-switch]');
  if (languageSwitch) languageSwitch.setAttribute('aria-label', config.languageLabel);
  document.querySelectorAll('[data-updated]').forEach(node => { node.textContent = config.updated; });
  const current = document.querySelector('.locale-section:not([hidden])');
  if (current) {
    const heading = current.querySelector('h1');
    const summary = current.querySelector('.lede');
    document.title = (heading ? heading.textContent : 'Yido') + ' · Yido';
    const meta = document.querySelector('meta[name="description"]');
    if (meta && summary) meta.content = summary.textContent;
  }
  for (const link of document.querySelectorAll('a[data-nav], a.brand, a.card')) {
    const url = new URL(link.getAttribute('href'), location.href);
    url.searchParams.set('lang', locale);
    link.href = url.href;
  }
  if (updateUrl) {
    const url = new URL(location.href);
    url.searchParams.set('lang', locale);
    url.hash = '';
    history.replaceState(null, '', url);
    remember(locale);
  }
}
activate(chooseInitial());
document.querySelectorAll('.locale-choice').forEach(link => {
  link.addEventListener('click', event => {
    event.preventDefault();
    activate(link.dataset.choose, true);
    window.scrollTo({top: 0, behavior: 'instant'});
  });
});
'''
    (ROOT / "assets" / "locale.js").write_text(js, encoding="utf-8")


if __name__ == "__main__":
    assert set(ORDER) == set(UI) == set(EXISTING) | set(ADDITIONAL)
    for slug, page, nav_index in PAGES:
        render(slug, page, nav_index)
    build_script()
