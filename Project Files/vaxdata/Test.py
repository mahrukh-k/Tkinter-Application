
from vaccination import vacs
from get_rent import medianrent


fips_code = '01101'

print(vacs(fips_code))
print(medianrent(fips_code))

fips_code = '48323'

print('\n')
print(vacs(fips_code))
print(medianrent(fips_code))