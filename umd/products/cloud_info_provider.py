from umd import system

package_mapping = {
    "centos7": ["cloud-info-provider"],
    "ubuntu14": ["python-cloud-info-provider"]}
package = package_mapping[system.distro_version]
