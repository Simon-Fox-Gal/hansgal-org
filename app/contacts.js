const forms = document.querySelectorAll('[data-contact-form]');
const started = Date.now();

async function contactEndpoint() {
  try {
    const base = document.querySelector('meta[name="hansgal-base"]')?.content || '';
    const response = await fetch(base + '/app/contact-config.json', {cache: 'no-cache'});
    if (!response.ok) return;
    const config = await response.json();
    if (config.endpoint && new URL(config.endpoint).protocol === 'https:') return config.endpoint;
  } catch {}
}

const endpoint = forms.length ? contactEndpoint() : Promise.resolve();

export async function sendContact(body, id) {
  const url = await endpoint || await contactEndpoint();
  if (!url) throw new Error('Contact service unavailable');

  const response = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({...body, id, language: document.documentElement.lang, elapsedMs: Date.now() - started}),
    credentials: 'omit',
    signal: AbortSignal.timeout(20000)
  });
  const result = await response.json();
  if (!response.ok || result.accepted !== true) throw new Error('Not accepted');
}

for (const form of forms) {
  const status = form.querySelector('[data-contact-status]');
  const submit = form.querySelector('button[type="submit"]');
  const membership = form.hasAttribute('data-membership-form');
  let busy = false;
  let key = '';

  form.addEventListener('input', () => { key = ''; });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !form.reportValidity()) return;

    const url = await endpoint;
    if (!url) {
      status.textContent = form.dataset.unavailable;
      return;
    }
    if (busy) return;
    busy = true;
    submit.disabled = true;
    status.textContent = form.dataset.sending;

    key ||= crypto.randomUUID();
    const body = Object.fromEntries(new FormData(form));
    if (membership) {
      body.message = 'Membership request: ' + body.membership;
      delete body.membership;
    }
    try {
      await sendContact(body, key);
      status.textContent = form.dataset.success;
      form.reset();
      key = '';
    } catch {
      status.textContent = form.dataset.error;
    } finally {
      busy = false;
      submit.disabled = false;
    }
  });
  endpoint.then(url => {
    if (!url) return;
    submit.disabled = false;
    status.textContent = '';
  });
}

for (const panel of document.querySelectorAll('[data-contact-panel]')) {
  const form = panel.querySelector('[data-contact-form]');
  for (const link of panel.querySelectorAll('[data-contact-person]')) {
    link.addEventListener('click', () => {
      form.elements.recipient.value = link.dataset.contactPerson;
      form.dispatchEvent(new Event('input'));
      form.elements.name.focus({preventScroll: true});
    });
  }
}
