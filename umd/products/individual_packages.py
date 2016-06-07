from umd import base


individual = base.Deploy(
    name="individual-packages",
    doc="Individual installation of packages.",
    need_cert=True,
    qc_step=["QC_DIST_1", "QC_FUNC_1"],
    qc_specific_id="mkgridmap"
)
