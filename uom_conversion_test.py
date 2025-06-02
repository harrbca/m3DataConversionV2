from dancik_uom import UOMService
import decimal
decimal.setcontext(decimal.Context(prec=6))


#uomService = UOMService("CASIMP10")
#print(uomService.convert(1, "CT", "SF"))  # Convert 90 SF to CT
#print(uomService.convert(51.33, "SF", "LB"))  # Convert 45 SF to LB


uomService_roll = UOMService("AFFASCFH572")
#print(uomService_roll.convert(1, "RL", "SY"))
#print(uomService_roll.convert(986.13, "IN", "SY"))
#print(uomService_roll.convert(986.13, "IN", "LF"))
print(uomService_roll.convert(788.04, "IN", "SY"))
#print(uomService_roll.convert(986.13, "IN", "RL"))

