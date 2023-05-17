

# Raise Invalid when not valid parameter is used
class Invalid(Exception):
    # Print cause of error
    print(Exception)
    pass


async def test_parameter_check(comb,order):
    if type(comb) == list:
        for i in comb:
            if type(i) != int:
                raise Invalid("comb list should countain only int, not valid unit {}".format(i)) 
    else:
        raise Invalid("Not a List, comb array should be list") # Not valid combination of arrays
    
    if type(order) == list:
        for i in comb:
            if type(i) != int:
                raise Invalid("Order list should countain string of Push and Pull, not valid unit --> {} <-- ".format(i)) # Not valid combination of arrays
    elif type(order) == "Push" or "Pull":
        pass
    else:
        raise Invalid("Invalid input") # Not valid combination of arrays