"""Shared public contact identities. Delivery addresses belong only on the server."""
PEOPLE = [
    ('general', 'Tanya Fox', 'Tanya', ['General enquiries and membership', 'Allgemeine Anfragen und Mitgliedschaft', 'Renseignements généraux et adhésion', '一般のお問い合わせ・入会']),
    ('recordings', 'Simon Fox', 'Simon', ['Recordings', 'Aufnahmen', 'Enregistrements', '録音について']),
    ('music', 'Eva Fox-Gál', 'Eva', ['Gál’s life, works and privately available music', 'Gáls Leben, Werke und privat erhältliche Noten', 'Vie et œuvres de Gál, partitions disponibles auprès de la famille', 'ガールの生涯・作品、家族から入手できる楽譜']),
    ('usa', 'Richard Marcus', 'Richard', ['USA enquiries', 'Anfragen aus den USA', 'Renseignements aux États-Unis', '米国からのお問い合わせ']),
]
COPY = {
 'en': ['Contact the Society', 'Choose whom to contact', 'Contact ', 'Your name', 'Your email address', 'Your message', 'Send message', 'Your message and contact details will be used to answer your enquiry.', 'If you have difficulty using the form, email', 'The contact form is not available at the moment. Please use the Society email below.', 'Sending…', 'Your message has been accepted for delivery. Thank you.', 'We could not confirm delivery. Your message is still here; please try again or use the Society email below.', 'Leave this empty'],
 'de': ['Kontakt zur Gesellschaft', 'Wählen Sie eine Ansprechperson', 'Kontakt: ', 'Ihr Name', 'Ihre E-Mail-Adresse', 'Ihre Nachricht', 'Nachricht senden', 'Ihre Nachricht und Kontaktdaten werden zur Beantwortung Ihrer Anfrage verwendet.', 'Falls Sie das Formular nicht verwenden können, schreiben Sie an', 'Das Kontaktformular ist zurzeit nicht verfügbar. Bitte nutzen Sie die unten angegebene E-Mail-Adresse der Gesellschaft.', 'Wird gesendet…', 'Ihre Nachricht wurde zur Zustellung angenommen. Vielen Dank.', 'Die Zustellung konnte nicht bestätigt werden. Ihre Nachricht bleibt erhalten. Bitte versuchen Sie es erneut oder nutzen Sie die unten angegebene E-Mail-Adresse.', 'Dieses Feld leer lassen'],
 'fr': ['Contacter la Société', 'Choisissez votre interlocuteur', 'Contacter ', 'Votre nom', 'Votre adresse électronique', 'Votre message', 'Envoyer le message', 'Votre message et vos coordonnées seront utilisés pour répondre à votre demande.', 'En cas de difficulté avec le formulaire, écrivez à', 'Le formulaire est momentanément indisponible. Veuillez utiliser l’adresse électronique de la Société ci-dessous.', 'Envoi en cours…', 'Votre message a été accepté pour acheminement. Merci.', 'Nous n’avons pas pu confirmer l’envoi. Votre message est conservé ici ; veuillez réessayer ou utiliser l’adresse électronique ci-dessous.', 'Laissez ce champ vide'],
 'ja': ['協会へのお問い合わせ', 'お問い合わせ先を選択', '連絡先：', 'お名前', 'メールアドレス', 'お問い合わせ内容', '送信', 'お問い合わせ内容と連絡先は、ご返信のために使用します。', 'フォームをご利用いただけない場合は、次のアドレスにメールをお送りください：', '現在、お問い合わせフォームはご利用いただけません。下記の協会のメールアドレスをご利用ください。', '送信中…', 'メッセージの送信を受け付けました。ありがとうございます。', '送信を確認できませんでした。入力内容はこの画面に残っています。再度お試しいただくか、下記のメールアドレスをご利用ください。', 'この欄は空欄のままにしてください'],
}

def context(language):
    index = ['en', 'de', 'fr', 'ja'].index(language)
    return {'contact_copy': COPY[language], 'contact_people': [
        {'id': id, 'name': name, 'first': first, 'role': roles[index]}
        for id, name, first, roles in PEOPLE
    ]}
