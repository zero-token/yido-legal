const ui = {"en":{"lang":"en","nav":["Privacy","Terms","Children's privacy","Support"],"updated":"Updated September 25, 2026","languageLabel":"Language"},"de":{"lang":"de","nav":["Datenschutz","Nutzungsbedingungen","Datenschutz für Kinder","Hilfe"],"updated":"Aktualisiert am 25. September 2026","languageLabel":"Sprache"},"es":{"lang":"es","nav":["Privacidad","Condiciones","Privacidad infantil","Ayuda"],"updated":"Actualizado el 25 de septiembre de 2026","languageLabel":"Idioma"},"es-419":{"lang":"es-419","nav":["Privacidad","Términos","Privacidad infantil","Ayuda"],"updated":"Actualizado el 25 de septiembre de 2026","languageLabel":"Idioma"},"fr":{"lang":"fr","nav":["Confidentialité","Conditions d’utilisation","Vie privée des enfants","Aide"],"updated":"Mis à jour le 25 septembre 2026","languageLabel":"Langue"},"hi":{"lang":"hi","nav":["गोपनीयता","उपयोग की शर्तें","बच्चों की गोपनीयता","सहायता"],"updated":"अपडेट: 25 सितंबर 2026","languageLabel":"भाषा"},"ja":{"lang":"ja","nav":["プライバシー","利用規約","子どものプライバシー","サポート"],"updated":"更新日：2026年9月25日","languageLabel":"言語"},"ko":{"lang":"ko","nav":["개인정보","이용약관","아동 개인정보","지원"],"updated":"최종 업데이트: 2026년 9월 25일","languageLabel":"언어"},"pt":{"lang":"pt-PT","nav":["Privacidade","Termos","Privacidade das crianças","Ajuda"],"updated":"Atualizado em 25 de setembro de 2026","languageLabel":"Idioma"},"pt-BR":{"lang":"pt-BR","nav":["Privacidade","Termos","Privacidade infantil","Ajuda"],"updated":"Atualizado em 25 de setembro de 2026","languageLabel":"Idioma"},"zh":{"lang":"zh-CN","nav":["隐私政策","用户协议","儿童隐私","支持"],"updated":"更新日期：2026 年 9 月 25 日","languageLabel":"语言"},"zh-Hant":{"lang":"zh-Hant","nav":["隱私權政策","使用條款","兒童隱私","支援"],"updated":"更新日期：2026 年 9 月 25 日","languageLabel":"語言"}};

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
