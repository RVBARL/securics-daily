FROM public.ecr.aws/o5x5t0j3/amd64/api_development:integration_test_securics-generic

ARG SECURICS_BRANCH

## install Securics
RUN mkdir securics && curl -sL https://github.com/wazuh/wazuh/tarball/${SECURICS_BRANCH} | tar zx --strip-components=1 -C securics
ADD base/agent/preloaded-vars.conf /securics/etc/preloaded-vars.conf
RUN /securics/install.sh

COPY base/agent/entrypoint.sh /scripts/entrypoint.sh

HEALTHCHECK --retries=900 --interval=1s --timeout=40s --start-period=30s CMD /usr/bin/python3 /tmp_volume/healthcheck/healthcheck.py || exit 1
