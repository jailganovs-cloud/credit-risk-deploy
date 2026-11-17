# Тегін Static Space арқылы жариялау

Сіздің экраныңызда Gradio және Docker ақылы болып шықты. Сондықтан осы
жаңартылған жобада тегін Static SDK қолданылады. Decision Tree браузердің
ішінде есептеледі. PRO жазылымы немесе GPU қажет емес.

## Hugging Face

1. Create a new Space бетінде Owner — jailganovs, Space name — credit-risk-demo.
2. SDK — Static. Template — Blank. Visibility — Public.
3. Create Space түймесін басыңыз.
4. Осы ZIP архивін компьютерде ашыңыз. Бұрынғы Gradio архивінің орнына осы
   жаңартылған архивті қолданыңыз.
5. Space ішіндегі Files → Add file → Upload files арқылы мына алты файлды
   жүктеңіз: README.md, index.html, ui.js, browser_model.js, model.json, examples.json.
6. Өзгерістерді Commit changes арқылы сақтаңыз. Қосымша ашылғанда екі дайын
   мысалды таңдап, Estimate model score батырмасын басыңыз.
   Күтілетін ұпайлар: 0.2487 және 0.8751. Скриншотын сақтаңыз.

## GitHub арқылы автоматты жаңарту

7. GitHub-та credit-risk-deploy атты repository ашыңыз. Негізгі branch — main.
8. Архивтен ашылған жоба файлдарын жүктеңіз. ZIP-тің өзін жүктемеңіз.
   .github/workflows/deploy.yml жолы міндетті түрде болуы керек. Жасырын папка
   жүктелмесе, Add file → Create new file арқылы осы толық атаумен жасаңыз.
9. Hugging Face Settings → Access Tokens арқылы осы Space-ке жазу құқығы бар
   token жасаңыз. Token-ді чатқа немесе кодқа жазбаңыз.
10. GitHub repository → Settings → Secrets and variables → Actions → Secrets:
    HF_TOKEN атымен secret қосып, token мәнін сонда сақтаңыз.
11. Variables бөлімінде HF_SPACE атымен айнымалы қосыңыз. Мәні:
    jailganovs/credit-risk-demo.
12. Actions → Test and deploy credit risk demo → Run workflow.
    test және deploy жұмыстары сәтті аяқталуын күтіңіз.
13. Автоматты жаңартуды дәлелдеу үшін GitHub-та index.html ішіндегі бір
    көрінетін мәтінді өзгертіп, main-ге сақтаңыз. Space-та жаңа мәтін көрінуі керек.

Есепті аяқтау үшін Space сілтемесі, GitHub repository сілтемесі, Actions run
сілтемелері, екі мысал нәтижесі және автоматты жаңарту дәлелі қажет.
Word есебі осы Static тәсіліне жаңартылды. Нақты жариялау дәлелдері әлі
қосылмағандықтан, оны әзірге соңғы submission ретінде жібермеңіз.
