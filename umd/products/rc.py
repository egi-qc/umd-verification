import re
import urllib2
import xml.etree.ElementTree as ET

from umd import api
from umd import base
from umd import config
from umd import system
from umd import utils


class RCDeploy(base.Deploy):
    from umd.products import bdii, gram5, globus, gridsite, wms, fts    # NOQA
    from umd.products import glexec, cream, arc, ui, canl, xrootd       # NOQA
    from umd.products import storm       				# NOQA

    product_mapping = {
        "site-bdii": bdii.bdii_site_puppet.metapkg,
        "top-bdii": bdii.bdii_top_puppet.metapkg,
        "Gram5": gram5.gram5.metapkg,
        "globus-default-security": globus.default_security.metapkg,
        "GridSite": gridsite.gridsite.metapkg,
        "wms-utils": wms.wms_utils.metapkg,
        "fts3": fts.fts.metapkg,
        "gLexec": glexec.glexec_wn.metapkg,
        "cream": cream.standalone.metapkg,
        "ARC": arc.arc_ce.metapkg,
        "gridFTP": globus.gridftp.metapkg,
        "Gfal2": ui.ui_gfal.metapkg,
        "cream-ge": cream.gridenginerized.metapkg,
        "Canl": canl.canl.metapkg,
        "gfal2-utils": ui.ui_gfal.metapkg,
        "xroot": xrootd.xrootd.metapkg,
        "storm": storm.storm.metapkg,
    }

    def _get_callback(self, url, from_major_release=None):
        """Get the callback URL from UMD repository feeds.

        :url: URL of the UMD repository feed.
        :from_major_release: Get all callbacks matching major release number.
        """
        response = urllib2.urlopen(url)
        txt = response.read()
        root = ET.fromstring(txt)

        l = []
        for p in root.iter('item'):
            s = re.search("Release: UMD-(\d\.\d\.\d)", p.find("title").text)
            if s:
                release = s.groups()[0]
                cb = p.find("distroAPICallBack").text
                if from_major_release:
                    major_release_no = config.CFG["rc_release"].split('.')[0]
                    if release.startswith(major_release_no):
                        l.append(cb)
                else:
                    if release == config.CFG["rc_release"]:
                        l.append(cb)
        return l

    def _get_product_list(self, urls):
        """Get the list of products given in a UMD callback url.

        :urls: List of the callback URLs.
        """
        # NOTE for scientific linux is 'sl' not 'redhat'
        if system.distro_version.startswith("redhat"):
            distro = [system.distro_version,
                      system.distro_version.replace("redhat", "sl")]
        else:
            distro = [system.distro_version]

        s = set()
        for url in urls:
            response = urllib2.urlopen(url)
            txt = response.read()
            root = ET.fromstring(txt)

            s = s.union([p.get("display")for p in root.iter("product")
                         if p.find("target").get("platform") in distro])
        return list(s)

    def pre_install(self):
        utils.enable_repo(config.CFG["repository_url"], name="UMD base RC")
        # Add IGTF repository as well (some products have dependencies on it)
        utils.enable_repo(config.CFG["igtf_repo"])
        # Products from production
        url_production = "http://admin-repo.egi.eu/feeds/production/"
        production_products = self._get_product_list(
            self._get_callback(
                url_production,
                from_major_release=config.CFG["umd_release"]))
        api.info("Products from production repository: %s"
                 % production_products)
        # Products from the candidate RC
        url_candidate = "http://admin-repo.egi.eu/feeds/candidate/"
        candidate_products = self._get_product_list(
            self._get_callback(url_candidate))
        api.info("Products from the candidate RC: %s" % candidate_products)
        # Merge them all
        products = production_products + candidate_products
        s = set()
        for product in products:
            try:
                s = s.union(self.product_mapping[product])
            except KeyError:
                s = s.union([product])
        config.CFG["metapkg"] = list(s)

    def _install(self, **kwargs):
        kwargs.update({
            "ignore_repos": True,
            "ignore_verification_repos": True})

        self.pre_install()
        base.installation.Install().run(**kwargs)
        self.post_install()


rc = RCDeploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    qc_step="QC_DIST_1",
)
