# #####==================================================
# '''
# save as TABLE time_QL, freq_QL, flux_QL
# '''
# #####==================================================
# CREATE DATABASE EOVSA_lightcurve_QL_db;

# USE EOVSA_lightcurve_QL_db;

# SHOW TABLES;



# CREATE TABLE Flare_IDs (
#     Flare_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
#     `Index` INT
# );


# CREATE TABLE time_QL (
#     Flare_ID BIGINT,
#     `Index` INT,
#     Time_JD DOUBLE,
#     PRIMARY KEY (Flare_ID, `Index`),
#     FOREIGN KEY (Flare_ID) REFERENCES Flare_IDs(Flare_ID)
# );


# CREATE TABLE freq_QL (
#     Flare_ID BIGINT,
#     `Index` INT,
#     Freq FLOAT,
#     PRIMARY KEY (Flare_ID, `Index`),
#     FOREIGN KEY (Flare_ID) REFERENCES Flare_IDs(Flare_ID)
# );

# CREATE TABLE flux_QL (
#     Flare_ID BIGINT,
#     `Index_f` INT,
#     `Index_t` INT,
#     flux FLOAT,
#     PRIMARY KEY (Flare_ID, `Index_f`, `Index_t`),
#     FOREIGN KEY (Flare_ID) REFERENCES Flare_IDs(Flare_ID)
# );




# # show columns from Flare_IDs;
# # SELECT * FROM Flare_IDs;

# # show columns from time_QL;

# # SELECT * FROM time_QL;
# # SELECT * FROM time_QL LIMIT 5, 10;

# # SELECT * FROM flux_QL LIMIT 5, 10;

# # drop table time_QL;


# # ##    flux DECIMAL(10,2),

# # SET GLOBAL innodb_lock_wait_timeout = 300;
# # SET GLOBAL wait_timeout = 300;

# # SHOW FULL PROCESSLIST;






#####==================================================
def rd_datfile(file):
    ''' Read EOVSA binary spectrogram file and return a dictionary with times 
        in Julian Date, frequencies in GHz, and cross-power data in sfu.
        
        Return Keys:
          'time'     Numpy array of nt times in JD format
          'fghz'     Numpy array of nf frequencies in GHz
          'data'     Numpy array of size [nf, nt] containing cross-power data
          
        Returns empty dictionary ({}) if file size is not compatible with inferred dimensions
    '''
    import struct
    import numpy as np
    def dims(file):
        # Determine time and frequency dimensions (assumes the file has fewer than 10000 times)
        f = open(file,'rb')
        tmp = f.read(83608)  # max 10000 times and 451 frequencies
        f.close()
        nbytes = len(tmp)
        tdat = np.array(struct.unpack(str(int(nbytes/8))+'d',tmp[:nbytes]))
        nt = np.where(tdat < 2400000.)[0]
        nf = np.where(np.logical_or(tdat[nt[0]:] > 18, tdat[nt[0]:] < 1))[0]
        return nt[0], nf[0]
    nt, nf = dims(file)
    f = open(file,'rb')
    tmp = f.read(nt*8)
    times = struct.unpack(str(nt)+'d',tmp)
    tmp = f.read(nf*8)
    fghz = struct.unpack(str(nf)+'d',tmp)
    tmp = f.read()
    f.close()
    if len(tmp) != nf*nt*4:
        print('File size is incorrect for nt=',nt,'and nf=',nf)
        return {}
    data = np.array(struct.unpack(str(nt*nf)+'f',tmp)).reshape(nf,nt)
    return {'time':times, 'fghz':fghz, 'data':data}


def spec_rebin(time, freq, spec, t_step=12, f_step=1, do_mean=True):
    """
    Rebin a spectrogram array to a new resolution in time and frequency.
    """
    import numpy as np
    tnum_steps = len(time) // t_step + (1 if len(time) % t_step != 0 else 0)
    fnum_steps = len(freq) // f_step + (1 if len(freq) % f_step != 0 else 0)

    time_new = np.array([time[i * t_step] for i in range(tnum_steps)])
    freq_new = np.array([freq[i * f_step] for i in range(fnum_steps)])

    spec_new = np.zeros((fnum_steps, tnum_steps))

    # Rebin the spectrogram
    if do_mean:
        for i in range(fnum_steps):
            for j in range(tnum_steps):
                spec_slice = spec[i * f_step:min((i + 1) * f_step, len(freq)),
                                 j * t_step:min((j + 1) * t_step, len(time))]
                spec_new[i, j] = np.mean(spec_slice)
    else:
        for i in range(fnum_steps):
            for j in range(tnum_steps):
                spec_new[i, j] = spec[i * f_step, j * t_step]

    return time_new, freq_new, spec_new





#####==================================================get flare_id_exist from mySQL
import mysql.connector
import os

connection = mysql.connector.connect(
    host=os.getenv('FLARE_DB_HOST'),
    database=os.getenv('FLARE_LC_DB_DATABASE'),
    user=os.getenv('FLARE_DB_USER'),
    password=os.getenv('FLARE_DB_PASSWORD')
)

cursor = connection.cursor()
cursor.execute("SELECT DISTINCT Flare_ID FROM freq_QL")
flare_id_exist = cursor.fetchall()




#####==================================================
import mysql.connector
from astropy.time import Time
import numpy as np
import sys
from datetime import datetime
import pandas as pd

# Connect to the database and get a cursor to access it:
cnxn = mysql.connector.connect(user='root', passwd='C@l1b4Me', host='localhost', database='EOVSA_lightcurve_QL_db')
# cnxn = mysql.connector.connect(user='Python3', passwd='Py+h0nUser', host='localhost', database='flare_test')



#####==================================================data preperation
from datetime import datetime, timedelta

# given_date = ['2019-01-01', '2024-02-15']##get index within this timerange
# given_date = [datetime.strptime(given_date[0], '%Y-%m-%d'), datetime.strptime(given_date[1], '%Y-%m-%d')]

file_path = '/data1/xychen/flaskenv/EOVSA_flare_list_from_wiki_sub.csv'#
df = pd.read_csv(file_path)

flare_id_tot = df['Flare_ID']
depec_file_tot = df['depec_file']
EO_tpeak_tot = df['EO_tpeak']

for i, date_str in enumerate(EO_tpeak_tot):
    datetp = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    if not any(int(flare_id_tot[i]) == existing_flare_id[0] for existing_flare_id in flare_id_exist):
    # if given_date[0] <= datetp <= given_date[1]:  # Check if the date is within the given range
        print("Flare_ID", int(flare_id_tot[i]))
        Flare_ID = int(flare_id_tot[i])
        depec_file = depec_file_tot[i]

        dsfile_path = '/common/webplots/events/'+ str(Flare_ID)[0:4] + '/' + depec_file + '.dat'
        try:
            data1 = rd_datfile(dsfile_path)

            time = data1['time'] ##in jd
            freq = np.array(data1['fghz'])
            spec = np.array(data1['data'])

            time_new, freq_new, spec_new = spec_rebin(time, freq, spec, t_step=4, f_step=1, do_mean=False)

            freq_plt = [3, 7, 11, 15]
            freq_QL = np.zeros(len(freq_plt))
            spec_QL = np.zeros((len(freq_plt), len(time_new)))

            for ff, fghz in enumerate(freq_plt):
                ind = np.argmin(np.abs(freq_new - fghz))
                # print(ind, fghz, freq_new[ind])
                freq_QL[ff] = freq_new[ind]
                spec_QL[ff,:] = spec_new[ind,:]

            time_QL = time_new
        except Exception as e:
            print("Errors of reading data - flux set to be 0")
            date_list = []
            for mm in range(20):
                date_list.append(datetp + timedelta(seconds=12*mm))
            time_QL = [date_obj.toordinal() + 1721425.5 for date_obj in date_list]
            freq_QL = [3, 7, 11, 15]
            spec_QL = np.zeros((len(freq_QL), len(time_QL)))+1e-3


        # #####==================================================
        # # cursor = cnxn.cursor()
        # # # cursor.execute("INSERT INTO Flare_IDs VALUES ()")
        # # # Flare_ID = cursor.lastrowid
        # # # Flare_ID = 20240101083000
        # # select_query = "SELECT * FROM Flare_IDs WHERE Flare_ID = %s"
        # # cursor.execute(select_query, (Flare_ID,))
        # # existing_records = cursor.fetchone()
        # # if existing_records:
        # #     delete_query = "DELETE FROM Flare_IDs WHERE Flare_ID = %s"
        # #     cursor.execute(delete_query, (Flare_ID,))


        # tables = ["time_QL", "freq_QL", "flux_QL", "Flare_IDs"]  # Child tables first, parent table last
        # cursor = cnxn.cursor()

        # for table in tables:
        #     # Check if Flare_ID already exists in the current table
        #     select_query = f"SELECT * FROM {table} WHERE Flare_ID = %s"
        #     cursor.execute(select_query, (Flare_ID,))
        #     existing_records = cursor.fetchall()
        #     # If Flare_ID exists, delete all related records
        #     if existing_records:
        #         print(f"To delete the {Flare_ID} in table ", table)
        #         delete_query = f"DELETE FROM {table} WHERE Flare_ID = %s"
        #         cursor.execute(delete_query, (Flare_ID,))
        # cnxn.commit()
        # cursor.close()

        cursor = cnxn.cursor()
        select_query = "SELECT * FROM Flare_IDs WHERE Flare_ID = %s"
        cursor.execute(select_query, (Flare_ID,))
        existing_records = cursor.fetchall()
        if existing_records:
            print(f"{Flare_ID} exist then jump to next ID ")
            continue
        cursor.close()



        #####==================================================
        cursor = cnxn.cursor()
        # insert_query = "INSERT INTO Flare_IDs (Flare_ID) VALUES (%s)"
        # cursor.execute(insert_query, (Flare_ID,))
        # cursor.execute("INSERT INTO Flare_IDs VALUES (%s, %s)", (Flare_ID, i+1))
        insert_query = "INSERT INTO Flare_IDs (Flare_ID, `Index`) VALUES (%s, %s)"
        cursor.execute(insert_query, (Flare_ID, i+1))

        cnxn.commit()
        cursor.close()

        #####==================================================
        # file_path = '/data1/xychen/flaskenv/spec_Tdata_QL/EOVSA_TPall_20220118_QLdata.npz'
        # npz = np.load(file_path, allow_pickle=True)
        # time_QL = npz['time_QL']
        # freq_QL = npz['freq_QL']
        # spec_QL = npz['spec_QL']

        #####=========================
        cursor = cnxn.cursor()
        for index, value in enumerate(time_QL):
            jd_time = value#Time(value).jd
            cursor.execute("INSERT INTO time_QL VALUES (%s, %s, %s)", (Flare_ID, index, jd_time))
        cnxn.commit()
        cursor.close()


        #####=========================
        cursor = cnxn.cursor()
        for index, value in enumerate(freq_QL):
            cursor.execute("INSERT INTO freq_QL VALUES (%s, %s, %s)", (Flare_ID, index, round(value, 3)))
        cnxn.commit()
        cursor.close()

        #####=========================
        cursor = cnxn.cursor()
        for ff, row in enumerate(spec_QL):
            # print(ff, len(row))
            for tt, value in enumerate(row):
                value = round(value, 3) if not np.isnan(value) else None  # Replace nan with None
                cursor.execute("INSERT INTO flux_QL VALUES (%s, %s, %s, %s)", (Flare_ID, ff, tt, value))
        cnxn.commit()
        cursor.close()

cnxn.close()




