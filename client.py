import xml.dom.minidom as xmd
import urllib2
import socket
import xml.etree.ElementTree as ET
import httplib

def discover():
    locations = []
    request = \
            'M-SEARCH * HTTP/1.1\r\n' \
            'HOST:239.255.255.250:1900\r\n' \
            'ST:upnp:rootdevice\r\n' \
            'MX:2\r\n' \
            'MAN:"ssdp:discover"\r\n' \
            '\r\n'

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(5)
    s.sendto(request, ('239.255.255.250', 1900))

    try:
        while True:
            data, addr = s.recvfrom(65507)
            locations.append(data.split("LOCATION:")[1].split("\n")[0])
    except socket.timeout:
        pass

    return locations

def grab_xml(xml_location):
    urls = []
    scpd_links = []
    control_links = []
    event_links = []
    
    response = urllib2.urlopen(xml_location)
    string = xmd.parseString(response.read())

    children = string.getElementsByTagName("SCPDURL")
        
        #print "children" + str(children)

    for step in children:
        scpd_links.append(step.firstChild.data)

    children = string.getElementsByTagName("controlURL")
        
    for step in children:
        control_links.append(step.firstChild.data)

    children = string.getElementsByTagName("eventSubURL")

    for step in children:
        event_links.append(step.firstChild.data)
        

    return (control_links, scpd_links, event_links)


def build_xml(host, urn_string, fn_string, *arguments):
    doc = xmd.Document()

    env = doc.createElementNS('', 's:Envelope')
    env.setAttribute('xmlns:s', 'http://schemas.xmlsoap.org/soap/envelope/')
    env.setAttribute('s:encodingStyle', 
            'http://schemas.xmlsoap.org/soap/encoding/')

    body = doc.createElementNS('', 's:Body')

    fn = doc.createElementNS('', 'u:' + fn_string)
    fn.setAttribute('xmlns:u', urn_string)

    arg_list = []

    for tag, arg in arguments:
        tmp_node = doc.createElement(tag)
        tmp_txt = doc.createTextNode(arg)
        tmp_node.appendChild(tmp_txt)
        arg_list.append(tmp_node)

    for element in arg_list:
        fn.appendChild(element)

    body.appendChild(fn)
    env.appendChild(body)
    doc.appendChild(env)

    pure_xml = doc.toxml()
    
    return pure_xml



dev_list = []
devices = discover()

for d in devices:
    dev_list.append(grab_xml(d))

for dev in dev_list:
    print "dev: " + str(dev)


