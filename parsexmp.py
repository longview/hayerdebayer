import xml.etree.ElementTree as ET
import json
def parsehuesat(root_d, count):
    hueSatDeltas = []

    for i in range(count):
        #hueSatDeltas.append([float(root_d[11][i].get('HueShift')), float(root_d[11][i].get('SatScale')), float(root_d[11][i].get('ValScale'))])
        hueSatDeltas.append(float(root_d[11][i].get('HueShift')))
    #for i in range(hueDivisions_d):
        hueSatDeltas.append(float(root_d[11][i].get('SatScale')))
    #for i in range(hueDivisions_d):
        hueSatDeltas.append(float(root_d[11][i].get('ValScale')))
    return hueSatDeltas

tree_w = ET.parse('HY-6110_3200k.xmp')
root_w = tree_w.getroot()
tree_d = ET.parse('HY-6110_6500k.xmp')
root_d = tree_d.getroot()

ccm_3000k = [[int(float(root_w[3][8].text)*10000), 10000], [int(float(root_w[3][7].text)*10000), 10000], [int(float(root_w[3][6].text)*10000), 10000],	
        [int(float(root_w[3][5].text)*10000), 10000], [int(float(root_w[3][4].text)*10000), 10000], [int(float(root_w[3][3].text)*10000), 10000],
        [int(float(root_w[3][2].text)*10000), 10000], [ int(float(root_w[3][1].text)*10000), 10000], [ int(float(root_w[3][0].text)*10000), 10000]]
ccm_5500k = [[int(float(root_d[3][8].text)*10000), 10000], [int(float(root_d[3][7].text)*10000), 10000], [int(float(root_d[3][6].text)*10000), 10000],	
        [int(float(root_d[3][5].text)*10000), 10000], [int(float(root_d[3][4].text)*10000), 10000], [int(float(root_d[3][3].text)*10000), 10000],
        [int(float(root_d[3][2].text)*10000), 10000], [ int(float(root_d[3][1].text)*10000), 10000], [ int(float(root_d[3][0].text)*10000), 10000]]
print('Warm CCM:')
print(ccm_3000k)
print('Cold CCM')
print(ccm_5500k)

with open('calibration/ccm_warm.json', 'w') as filehandle:
    json.dump(ccm_3000k, filehandle)
with open('calibration/ccm_cold.json', 'w') as filehandle:
    json.dump(ccm_5500k, filehandle)

hueDivisions_w = int(root_w[11].get('hueDivisions'))
satDivisions_w = int(root_w[11].get('satDivisions'))
valDivisions_w = int(root_w[11].get('valDivisions'))
hueDivisions_d = int(root_d[11].get('hueDivisions'))
satDivisions_d = int(root_d[11].get('satDivisions'))
valDivisions_d = int(root_d[11].get('valDivisions'))


hueSatDeltas_w = parsehuesat(root_w, hueDivisions_w*satDivisions_w)
print('Warm huesat ' + str(hueDivisions_w) + ' ' + str(satDivisions_w) + ' ' + str(valDivisions_w))
#print(hueSatDeltas_w)

hueSatDeltas_d = parsehuesat(root_d, hueDivisions_d*satDivisions_d)
print('Cold huesat ' + str(hueDivisions_d) + ' ' + str(satDivisions_d) + ' ' + str(valDivisions_d))
#print(hueSatDeltas_d)

with open('calibration/warm_huesat.json', 'w') as filehandle:
    json.dump(hueSatDeltas_w, filehandle)
with open('calibration/cold_huesat.json', 'w') as filehandle:
    json.dump(hueSatDeltas_d, filehandle)

toneCurve = []
for i in range(int(root_d[12].get('Size'))):
    toneCurve.append(float(root_d[12][i].get('h')))
    toneCurve.append(float(root_d[12][i].get('v')))

with open('calibration/tonecurve.json', 'w') as filehandle:
    json.dump(hueSatDeltas_d, filehandle)