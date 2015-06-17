from umd.base import Deploy


crl = Deploy(
        name="ca",
        doc="CA/CRL deployment.",
        metapkg=["ca-policy-egi-core", "fetch-crl"],
        has_infomodel=False,
        qc_specific_id="ca"
)
