import {sendContact} from './contacts.js?v=3';

const support = document.getElementById('hgs-donate');
const choice = document.getElementById('hgs-join-choice');
const membership = document.getElementById('hgs-membership-form');
const gift = document.getElementById('hgs_giftaid_form');
const optIn = document.getElementById('hgs-gift-choice');
const previousLink = support.querySelector('[data-gift-previous]');
const inlineSlot = support.querySelector('[data-gift-inline]');
const pastSlot = support.querySelector('[data-gift-outside]');
const pastFields = gift.querySelector('[data-gift-past-fields]');
const overseas = gift.querySelector('[data-gift-overseas]');
const status = gift.querySelector('[data-gift-status]');
const sendButton = gift.querySelector('button[type="submit"]');
const paypal = support.querySelector('.hgs-paypal-form');
const payButton = paypal.querySelector('button[type="submit"]');
const controls = gift.elements;
let member = {};
let mode = 'none';
let request;
let busy = false;

function prefill() {
  const bankEmail = support.querySelector('[data-bank-request] input[name="email"]');
  controls.name.value ||= membership.elements.name.value || member.name || '';
  controls.email.value ||= membership.elements.email.value || member.email || bankEmail?.value || '';
}

function disclose(next, focus = false) {
  if (next === mode) return;
  const past = next === 'past';
  mode = next;
  optIn.checked = next === 'current';
  previousLink.setAttribute('aria-expanded', String(past));
  pastFields.hidden = pastFields.disabled = !past;
  (past ? pastSlot : inlineSlot).append(gift);
  gift.hidden = next === 'none';
  status.textContent = '';
  if (gift.hidden) return;
  controls.confirm.checked = false;
  prefill();
  if (focus) gift.querySelector('[data-gift-heading]').focus();
}

function openFromAnchor() {
  if (location.hash === '#hgs-join') choice.checked = true;
  if (location.hash === '#hgs-donate') choice.checked = false;
  if (location.hash === '#hgs-giftaid') disclose('past');
  else if (mode === 'past') disclose('none');
}

document.querySelectorAll('.hgs-top-card a[href="#hgs-join"], .hgs-top-card a[href="#hgs-donate"]').forEach(link => {
  link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    choice.checked = link.hash === '#hgs-join';
  });
});
window.addEventListener('hashchange', openFromAnchor);
openFromAnchor();

membership.addEventListener('submit', () => {
  member = {name: membership.elements.name.value, email: membership.elements.email.value};
  if (!gift.hidden) prefill();
});

optIn.addEventListener('change', () => {
  if (location.hash === '#hgs-giftaid') history.replaceState(null, '', '#hgs-donate');
  disclose(optIn.checked ? 'current' : 'none');
});

previousLink.addEventListener('click', event => {
  if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (busy) { event.preventDefault(); return; }
  if (mode === 'past') {
    event.preventDefault();
    history.replaceState(null, '', '#hgs-donate');
    disclose('none');
  } else {
    disclose('past', true);
  }
});

function setAddressFields() {
  const residence = controls.residence.value;
  overseas.hidden = overseas.disabled = residence === 'uk';
  controls.postcode.parentElement.hidden = controls.postcode.disabled = residence === 'islands';
  controls.postcode.required = residence === 'uk';
}
controls.residence.addEventListener('change', setAddressFields);
setAddressFields();

function setCurrencyField() {
  const other = !controls.currency.value;
  controls.otherCurrency.parentElement.hidden = controls.otherCurrency.disabled = !other;
  controls.otherCurrency.required = other;
}
controls.currency.addEventListener('change', setCurrencyField);
setCurrencyField();

function paymentDetails(data) {
  if (mode === 'past') {
    const currency = data.currency || data.otherCurrency.toUpperCase();
    return [
      'Earlier donation: ' + data.date + ', ' + currency + ' ' + data.amount,
      data.paymentReference && 'Earlier payment reference: ' + data.paymentReference
    ];
  }
  const value = id => document.getElementById(id).value.trim();
  const amount = value('hgs_donation_amount');
  return [
    amount && 'Intended amount: ' + value('hgs_currency') + ' ' + amount,
    'Payment method: ' + value('hgs_payment_method')
  ];
}

function showReference() {
  const method = document.getElementById('hgs_payment_method').value;
  const wording = mode === 'current' && ['Bank transfer','Cheque'].includes(method) ? gift.dataset.bankReference : gift.dataset.reference;
  status.textContent = gift.dataset.sent + ' ' + wording.replace('{reference}', request.reference);
  return request.reference;
}

async function saveDeclaration() {
  if (busy || !gift.reportValidity()) return;
  const data = Object.fromEntries([...new FormData(gift)].map(([key, value]) => [key, value.trim()]));
  const details = paymentDetails(data).filter(Boolean);
  const signature = JSON.stringify([data, details]);
  if (request?.signature !== signature) {
    const id = crypto.randomUUID();
    request = {id, signature, date: new Date().toISOString(), reference: 'HGS-' + id.replaceAll('-', '').slice(0, 12).toUpperCase()};
  }
  if (request.accepted) return showReference();

  const declaration = [
    'Gift Aid declaration — Hans Gál Society',
    'Reference: ' + request.reference,
    'Declared at: ' + request.date,
    'Name: ' + data.name,
    'Home address: ' + [data.address, data.town, data.region, data.postcode, data.country || gift.dataset.ukTerritory].filter(Boolean).join(', '),
    'Residence: ' + (data.residence === 'uk' ? 'UK' : 'Non-UK donor'),
    ...details,
    '',
    gift.querySelector('[data-gift-scope="' + data.scope + '"]').textContent,
    gift.querySelector('#hgs-gift-tax').textContent,
    gift.querySelector('[data-gift-confirm]').textContent
  ].join('\n');

  busy = sendButton.disabled = payButton.disabled = optIn.disabled = true;
  status.textContent = gift.dataset.sending;
  try {
    await sendContact({recipient: 'general', name: data.name, email: data.email, message: declaration, website: data.website}, request.id);
    request.accepted = true;
    return showReference();
  } catch {
    status.textContent = gift.dataset.error;
  } finally {
    busy = sendButton.disabled = payButton.disabled = optIn.disabled = false;
  }
}

gift.addEventListener('submit', event => {
  event.preventDefault();
  void saveDeclaration();
});

paypal.addEventListener('submit', async event => {
  if (event.defaultPrevented || mode !== 'current') return;
  event.preventDefault();
  const reference = await saveDeclaration();
  if (!reference || mode !== 'current') return;
  paypal.elements.item_name.value += ' - ' + reference;
  paypal.target = '_self';
  paypal.submit();
});
