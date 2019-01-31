#!/user/bin/env python

from dnac import Dnac
from template import Template, TARGET_BY_ID

MODULE="template_example.py"

print "%s: preparing to deploy a template..." % MODULE

dnac = Dnac()

template = Template(dnac, "MGM Set VLAN")

print "%s: setting the target device..." % MODULE

dnac.api['MGM Set VLAN'].targetId = "a0116157-3a02-4b8d-ad89-45f45ecad5da"
dnac.api['MGM Set VLAN'].targetType = TARGET_BY_ID

print "%s: setting the template's parameters..." % MODULE

dnac.api['MGM Set VLAN'].versionedTemplateParams['interface'] = "g1/0/8"
dnac.api['MGM Set VLAN'].versionedTemplateParams['description'] = \
    "Provisioned by %s" % MODULE
dnac.api['MGM Set VLAN'].versionedTemplateParams['vlan'] = 10

print "%s: deploying the template..." % MODULE

dnac.api['MGM Set VLAN'].deploySync()

print "%s: deploy results: %s" % \
       (MODULE, dnac.api['MGM Set VLAN'].deployment.results)

print
