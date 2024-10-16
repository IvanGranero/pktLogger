import pandas as pd

class DataFrameProvider:
    def __init__(self):
        self.alldata = pd.DataFrame() # Dataframe to be used across clasess by sharing the same instance

    def clear_data(self):
        del self.alldata
        self.alldata = pd.DataFrame()

    def save_packets(self, file_name):
        print ("Saving log to a file")
        #save all buffer into file
        #alldata.to_csv(file_name) 
        # PARQUET GIVING ERROR for unknown values, NEED TOF IND A WAY TO SAVE IGNORING ERRORS     
        self.alldata = self.alldata.convert_dtypes()
        try:        
            self.alldata.to_parquet(file_name+'.parquet.gzip', compression='gzip')
        except Exception as e:
            try:
                print(e)
                self.alldata.to_csv(file_name+'.gzip', compression='gzip')
            except Exception as e:
                print(e)
                self.alldata.to_csv(file_name+'.csv', sep='\t')
        print("Saved as bufferdump.")

    def df_toJSON(self):
        try:
            datos = self.alldata.head(5)
            datos = datos.to_json(default_handler=str, orient="records")
        except Exception as e:
            print (e)
        return datos

    def query_filter(self, filter_argument):
        #return self.alldata.query(filter_argument)
        ## Need to sanitize the input to avoid code injection
        return eval(filter_argument, {'data': self.alldata})    

    def eval_filter(self, filter_argument):
        return pd.eval(filter_argument)

    # maybe change them to another python file to add all the analysis decoders such as base64

    def add_ascii_column(self, column_source):
        self.alldata['dataascii'] = self.alldata[column_source].apply(self.to_ascii)
        self.alldata['dataascii'] = self.alldata['dataascii'].astype(str)

    def to_ascii(self, datahex):
        return ''.join(
            chr(int(datahex[i:i + 2], 16)) if 32 <= int(datahex[i:i + 2], 16) <= 126 else '.'
            for i in range(0, len(datahex), 2)
        )
