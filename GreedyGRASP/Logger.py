import sys

class Logger(object):
    def __init__(self, fields):
        self._fields = []
        self._fieldNames = []
        self._fieldValues = []

        if(type(fields) != list):
            raise Exception('[Logger.__init__] Attribute "fields" must be a list and each entry should contain a dictionary with attributes "id", "name", "headerformat" and "valueformat"')

        for field in fields:
            if(type(field['id']) != str): raise Exception('[Logger.__init__] Field "id" must be a string')
            if(type(field['name']) != str): raise Exception('[Logger.__init__] Field "name" must be a string')
            if(type(field['headerformat']) != str): raise Exception('[Logger.__init__] Field "headerformat" must be a string')
            if(type(field['valueformat']) != str): raise Exception('[Logger.__init__] Field "valueformat" must be a string')
            fieldName = field['headerformat'].format(field['name'])
            self._fields.append({ 'id':field['id'], 'name':fieldName, 'format':field['valueformat'] })
            self._fieldNames.append(fieldName)

    def printHeaders(self):
        print('   '.join(self._fieldNames))
        sys.stdout.flush()

    def printValues(self, fieldValues):
        if(type(fieldValues) != dict):
            raise Exception('[Logger.printValues] Attribute "fieldValues" must be a dictionary indexed by field id and the field value as value')
        
        values = []
        for field in self._fields:
            fieldId = field['id']
            fieldFormat = field['format']
            if(fieldId not in fieldValues):
                raise Exception('[Logger.printValues] No value has not been provided for field "%s"' % fieldId)
            
            value = fieldValues[fieldId]
            value = fieldFormat.format(value)
            values.append(value)
        
        print('   '.join(values))
        sys.stdout.flush()

        self._fieldValues.append(values)
