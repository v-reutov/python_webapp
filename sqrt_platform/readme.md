Sqrt_platform is a django-based app for computing square roots out of real or complex numbers or expressions.

Requirements:
    python 3.6
    django 1.11
    mpmath
    wolframalpha


If you are looking for knowledge about django, visit https://docs.djangoproject.com/ for tutorials, reference and topic and how-to guides.

If you are looking for an step-by-step tutorial for non-programmers, visit https://tutorial.djangogirls.org/.

App tree:
├───core                core functionality of app - square root computing
├───locale              internationalization files. Details: https://docs.djangoproject.com/en/1.11/topics/i18n/
├───migrations          not used
├───static
│   └───sqrt_platform   static files for front-end: js, css
├───templates
│   └───sqrt_platform   html templates for front-end
├───admin.py            not used
├───apps.py             connfig class
├───models.py           not used
├───tests.py            core functionality tests
├───urls.py             url dispatcher
└───views.py            http-request handlers
