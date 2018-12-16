# Validate instance attributes read from a DAT file.
# It validates the structure of the parameters read from the DAT file.
# It does not validate that the instance is feasible or not.
# Use Problem.checkInstance() function to validate the feasibility of the instance.
class ValidateInputData(object):
    @staticmethod
    def validate(data):
        # Validate that all input parameters were found
        for paramName in ['nServices', 'nDrivers', 'nBuses', 'maxBuses', 'BM', 'CBM', 'CEM', 'ST', 'DM', 'DK', 'NP', 'cap', 'eurosMin', 'eurosKm', 'maxD']:
            if(not data.__dict__.has_key(paramName)):
                raise Exception('Parameter/Set(%s) not contained in Input Data' % str(paramName))

        # Validate nServices
        nServices = data.nServices
        if(not isinstance(nServices, int) or (nServices <= 0)):
            raise Exception('nServices(%s) has to be a positive integer value.' % str(nServices))
        
        # Validate nDrivers
        nDrivers = data.nDrivers
        if(not isinstance(nDrivers, int) or (nDrivers <= 0)):
            raise Exception('nDrivers(%s) has to be a positive integer value.' % str(nDrivers))

        # Validate nBuses
        nBuses = data.nBuses
        if (not isinstance(nBuses, int) or (nBuses <= 0)):
            raise Exception('nBuses(%s) has to be a positive integer value.' % str(nBuses))

        # Validate maxBuses
        maxBuses = data.maxBuses
        if (not isinstance(maxBuses, int) or (maxBuses <= 0)):
            raise Exception('maxBuses(%s) has to be a positive integer value.' % str(maxBuses))

        # Validate BM
        BM = data.BM
        if(not isinstance(BM, int) or (BM <= 0)):
            raise Exception('BM(%s) has to be a positive integer value.' % str(BM))

        # Validate CBM
        CBM = data.CBM
        if (not isinstance(CBM, (int,float)) or (CBM <= 0)):
            raise Exception('CBM(%s) has to be a positive integer value.' % str(CBM))

        # Validate CEM
        CEM = data.CEM
        if (not isinstance(CEM, (int, float)) or (CEM <= 0)):
            raise Exception('CEM(%s) has to be a positive integer value.' % str(CEM))

        # Validate ST
        ST = data.ST
        if (len(ST) != nServices):
            raise Exception('Size of ST(%d) does not match with value of nThreads(%d).' % (len(ST), nServices))

        for value in ST:
            if(not isinstance(value, int) or (value < 0)):
                raise Exception('Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))

        # Validate DM
        DM = data.DM
        if (len(DM) != nServices):
            raise Exception('Size of DM(%d) does not match with value of nThreads(%d).' % (len(DM), nServices))

        for value in DM:
            if(not isinstance(value, int) or (value < 0)):
                raise Exception('Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))

        # Validate DK
        DK = data.DK
        if (len(DK) != nServices):
            raise Exception('Size of DK(%d) does not match with value of nThreads(%d).' % (len(DK), nServices))

        for value in DK:
            if(not isinstance(value, int) or (value < 0)):
                raise Exception('Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))

        # Validate NP
        NP = data.NP
        if (len(NP) != nServices):
            raise Exception('Size of NP(%d) does not match with value of nThreads(%d).' % (len(NP), nServices))

        for value in NP:
            if(not isinstance(value, int) or (value < 0)):
                raise Exception('Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))

        # Validate cap
        cap = data.cap
        if (len(cap) != nServices):
            raise Exception('Size of cap(%d) does not match with value of nThreads(%d).' % (len(cap), nBuses))

        for value in cap:
            if (not isinstance(value, int) or (value < 0)):
                raise Exception(
                    'Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))

        # Validate eurosMin
        eurosMin = data.eurosMin
        if (len(eurosMin) != nServices):
            raise Exception('Size of eurosMin(%d) does not match with value of nThreads(%d).' % (len(eurosMin), nBuses))

        for value in eurosMin:
            if (not isinstance(value, float) or (value < 0)):
                raise Exception(
                    'Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))
            
        # Validate eurosKm
        eurosKm = data.eurosKm
        if (len(eurosKm) != nServices):
            raise Exception('Size of eurosKm(%d) does not match with value of nThreads(%d).' % (len(eurosKm), nBuses))

        for value in eurosKm:
            if (not isinstance(value, float) or (value < 0)):
                raise Exception(
                    'Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))
            
        # Validate maxD
        maxD = data.maxD
        if (len(maxD) != nDrivers):
            raise Exception('Size of maxD(%d) does not match with value of nThreads(%d).' % (len(maxD), nBuses))

        for value in maxD:
            if (not isinstance(value, float) or (value < 0)):
                raise Exception(
                    'Invalid parameter value(%s) in rh. Should be a float greater or equal than zero.' % str(value))