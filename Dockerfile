FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system ssg && adduser --system --ingroup ssg ssg

COPY pyproject.toml README.md ./
COPY ssg ./ssg

RUN pip install --upgrade pip && \
    pip install . && \
    ssg --help

WORKDIR /site

COPY --chown=ssg:ssg example-site ./
RUN chown ssg:ssg /site

USER ssg

RUN ssg build /site && test -f /site/dist/index.html && test -f /site/dist/feed.xml

ENTRYPOINT ["ssg"]
CMD ["build", "/site"]
