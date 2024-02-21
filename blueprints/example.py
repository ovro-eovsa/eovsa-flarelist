import numpy as np
import pandas as pd
from flask import Flask, Blueprint, render_template, request, jsonify
import plotly.express as px
import plotly.graph_objects as go
import socket
import json
import plotly
import os
import mysql.connector
from astropy.time import Time

example = Blueprint('example', __name__, template_folder='templates')

def get_eo_flare_list_MySQL(start_utc, end_utc):
    """
    info from MySQL
    """
    connection = mysql.connector.connect(
        host=os.getenv('FLARE_DB_HOST'),
        database=os.getenv('FLARE_DB_DATABASE'),
        user=os.getenv('FLARE_DB_USER'),
        password=os.getenv('FLARE_DB_PASSWORD')
    )

    cursor = connection.cursor()

    # cursor.execute("SHOW COLUMNS FROM EOVSA_flare_list_wiki_tb")
    # columns = cursor.fetchall()
    # for column in columns:
    #     print(column)

    cursor.execute("SELECT Flare_ID FROM EOVSA_flare_list_wiki_tb")
    flare_id = cursor.fetchall()

    cursor.execute("SELECT Flare_class FROM EOVSA_flare_list_wiki_tb")
    GOES_class = cursor.fetchall()

    cursor.execute("SELECT EO_tstart FROM EOVSA_flare_list_wiki_tb")
    EO_tstart = np.array(cursor.fetchall())  ##in Julian Dates i.e., Time('2019-04-15 19:30:04').jd

    cursor.execute("SELECT EO_tend FROM EOVSA_flare_list_wiki_tb")
    EO_tend = np.array(cursor.fetchall())

    cursor.execute("SELECT depec_file FROM EOVSA_flare_list_wiki_tb")
    depec_file1 = cursor.fetchall()
    depec_file = [item[0] for item in depec_file1]

    cursor.close()
    connection.close()

    # Time(EO_tstart[0],format='jd').isot

    t_st = Time(start_utc).jd
    t_ed = Time(end_utc).jd

    ind = np.where((EO_tstart <= t_ed) & (t_st <= EO_tend))[0]

    result = []
    keys = ['_id', 'start', 'end', 'link']
    keys = ['_id', 'flare_id', 'start', 'end', 'GOES_class', 'link_dspec_data', 'link_movie', 'link_fits']
    # keys=['_id','flare_id','start','end','GOES_class','link_dspec','link_dspec_data','link_movie','link_fits']
    if ind.size > 0:
        for i, j in enumerate(ind):
            flare_id_str = str(flare_id[j][0])

            link_dspec_str = f'http://www.ovsa.njit.edu/wiki/index.php/File:' + depec_file[
                j] + '.png'  ##http://www.ovsa.njit.edu/wiki/index.php/File:EOVSA_20220118_Mflare.png
            # link_dspec_str = f'http://www.ovsa.njit.edu/wiki/index.php/File:EOVSA_{flare_id_str[0:4]}{flare_id_str[4:6]}{flare_id_str[6:8]}_'+GOES_class[j][0]+'flare.png'
            link_dspec_data_str = f'http://ovsa.njit.edu/events/{flare_id_str[0:4]}/'  # EOVSA_{flare_id_str[0:4]}_??flare.dat
            link_movie_str = f'http://ovsa.njit.edu/SynopticImg/eovsamedia/eovsa-browser/{flare_id_str[0:4]}/{flare_id_str[4:6]}/{flare_id_str[6:8]}/eovsa.lev1_mbd_12s.flare_id_{flare_id_str}.mp4'
            link_fits_str = f'http://ovsa.njit.edu/fits/flares/{flare_id_str[0:4]}/{flare_id_str[4:6]}/{flare_id_str[6:8]}/{flare_id_str}/'

            result.append({'_id': i + 1,
                           'flare_id': int(flare_id[j][0]),
                           'start': Time(EO_tstart[j], format='jd').isot[0].split('.')[0],
                           'end': Time(EO_tend[j], format='jd').isot[0].split('.')[0],
                           'GOES_class': GOES_class[j][0],
                           'link_dspec': '<a href="' + link_dspec_str + '">DSpec</a>',
                           'link_dspec_data': '<a href="' + link_dspec_data_str + '">DSpec_Data</a>',
                           'link_movie': '<a href="' + link_movie_str + '">QL_Movie</a>',
                           'link_fits': '<a href="' + link_fits_str + '">FITS</a>'
                           })
    return result


def get_eo_dspec_QL(start_utc, end_utc):
    """
    return the tim_plt, freq_plt, spec_plt
    """
    from astropy.io import fits
    from astropy.time import Time
    import os
    import pandas as pd
    t_st = pd.to_datetime(start_utc)
    t_ed = pd.to_datetime(end_utc)

    dates = pd.date_range(t_st, t_ed)

    all_times_isot = []
    all_specs = []

    for date in dates:
        year, month, day = f"{date.year:04d}", f"{date.month:02d}", f"{date.day:02d}"
        # year, month, day = str(t_st.year), '{:02d}'.format(t_st.month), '{:02d}'.format(t_st.day)
        # file_path = os.path.join('/data1/eovsa/fits/synoptic/', year, month, day)
        # file_name = 'EOVSA_XPall_' + year + month + day + '.fts'

        # file_path = '/data1/xychen/flaskenv/spec_Xdata_QL/EOVSA_XPall_' + year + month + day + '_QLdata.npz'
        file_path = '/common/webplots/TPall_QL/EOVSA_TPall_' + year + month + day + '_QLdata.npz'

        try:
            npz = np.load(file_path, allow_pickle=True)
            time_QL = npz['time_QL']
            freq_QL = npz['freq_QL']
            spec_QL = npz['spec_QL']

            tim_plt_isot = Time(time_QL).isot
            freq_plt = freq_QL
            spec_plt = spec_QL

            ##=========================
            all_times_isot.append(tim_plt_isot)
            all_specs.append(spec_plt)
        except FileNotFoundError:
            print(f"File {file_path} not found. Skipping to next file.")
            continue

    tim_plt_isot = Time(np.concatenate(all_times_isot)).isot
    spec_plt = np.concatenate(all_specs, axis=1)

    spec_data = {'tim_plt_isot': tim_plt_isot.tolist(), 'freq_plt': freq_plt.tolist(), 'spec_plt': spec_plt.tolist()}

    return spec_data


@example.route("/api/flare/query", methods=['POST'])
def get_flare_list_from_database():
    try:
        start = request.form['start']
        end = request.form['end']
        if not start or not end:
            raise ValueError("Start and end times are required.")

        result = get_eo_flare_list_MySQL(start, end)
        return jsonify({"result": result})

    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {e}")
        # Return a JSON response with the error message
        return jsonify({"error": str(e)}), 500


##=========================
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
        f = open(file, 'rb')
        tmp = f.read(83608)  # max 10000 times and 451 frequencies
        f.close()
        nbytes = len(tmp)
        tdat = np.array(struct.unpack(str(int(nbytes / 8)) + 'd', tmp[:nbytes]))
        nt = np.where(tdat < 2400000.)[0]
        nf = np.where(np.logical_or(tdat[nt[0]:] > 18, tdat[nt[0]:] < 1))[0]
        return nt[0], nf[0]

    nt, nf = dims(file)
    f = open(file, 'rb')
    tmp = f.read(nt * 8)
    times = struct.unpack(str(nt) + 'd', tmp)
    tmp = f.read(nf * 8)
    fghz = struct.unpack(str(nf) + 'd', tmp)
    tmp = f.read()
    f.close()
    if len(tmp) != nf * nt * 4:
        print('File size is incorrect for nt=', nt, 'and nf=', nf)
        return {}
    data = np.array(struct.unpack(str(nt * nf) + 'f', tmp)).reshape(nf, nt)
    return {'time': times, 'fghz': fghz, 'data': data}


@example.route('/fetch-spectral-data/<flare_id>', methods=['GET'])
# #####=========================click on flare ID and show its corresponding flux curves
def fetch_spectral_data(flare_id):
    #####=========================
    ##Connect to the MySQL database

    connection = mysql.connector.connect(
        host=os.getenv('FLARE_DB_HOST'),
        database=os.getenv('FLARE_LC_DB_DATABASE'),
        user=os.getenv('FLARE_DB_USER'),
        password=os.getenv('FLARE_DB_PASSWORD')
    )

    given_flare_id = int(flare_id)

    cursor = connection.cursor()
    #####=========================
    cursor.execute("SELECT * FROM time_QL WHERE Flare_ID = %s", (given_flare_id,))
    records = cursor.fetchall()
    # jd_times = []  # List to store jd_time values
    # for record in records:
    #     # Assuming jd_time is the third column (index 2) in the table
    #     jd_time = record[2]
    #     jd_times.append(jd_time)
    # time1 = jd_times
    time1 = [record[2] for record in records]

    #####=========================
    cursor.execute("SELECT * FROM freq_QL WHERE Flare_ID = %s", (given_flare_id,))
    records = cursor.fetchall()
    # Extract the values from the fetched records
    fghz = [record[2] for record in records]

    #####=========================
    cursor.execute("SELECT * FROM flux_QL WHERE Flare_ID = %s", (given_flare_id,))
    records = cursor.fetchall()

    spec_QL = []
    # Iterate over the retrieved records and reconstruct the array
    for record in records:
        Flare_ID, Index_f, Index_t, flux = record
        while len(spec_QL) <= Index_f:
            spec_QL.append([])
        while len(spec_QL[Index_f]) <= Index_t:
            spec_QL[Index_f].append(None)
        spec_QL[Index_f][Index_t] = flux

    spec = np.array(spec_QL)

    cursor.close()
    connection.close()

    #####=========================
    from astropy.time import Time
    tim_plt_datetime = pd.to_datetime(Time(time1, format='jd').isot)
    # tim_plt_datetime = ["2021-01-01T00:00:00", "2021-01-01T00:01:00", "2021-01-01T00:02:00"]

    spec_plt_log = spec
    freq_plt = fghz

    # Create the Plotly figure
    fig = go.Figure()

    # Plot the spectral data
    # fig.add_trace(go.Scatter(x=tim_plt_datetime, y=spec_plt_log, mode='lines', name='Spectral Data'))
    fig.add_trace(go.Scatter(x=tim_plt_datetime, y=spec_plt_log[0, :], mode='lines', name=f"{freq_plt[0]:.1f} GHz"))
    fig.add_trace(go.Scatter(x=tim_plt_datetime, y=spec_plt_log[1, :], mode='lines', name=f"{freq_plt[1]:.1f} GHz"))
    fig.add_trace(go.Scatter(x=tim_plt_datetime, y=spec_plt_log[2, :], mode='lines', name=f"{freq_plt[2]:.1f} GHz"))
    fig.add_trace(go.Scatter(x=tim_plt_datetime, y=spec_plt_log[3, :], mode='lines', name=f"{freq_plt[3]:.1f} GHz"))

    # Update layout
    fig.update_layout(
        title=f'Flux Data for Flare ID: {flare_id}',
        xaxis_title="Time [UT]",
        yaxis_title="Flux [sfu]",
        xaxis_tickformat='%H:%M',
        template="plotly"  # or choose another template that fits your web design
    )

    # Convert Plotly figure to HTML
    plot_html_ID = fig.to_html(full_html=False)  # , include_plotlyjs=False
    print(f"Flare ID {flare_id}: fetch-spectral-data success")

    # # Return the plot's HTML for dynamic insertion into the webpage
    plot_data_ID = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify({"plot_data_ID": plot_data_ID})


# route example
@example.route("/")
def render_example_paper():
    hostname = socket.gethostname()
    return render_template('index.html', result=[], plot_html_ID=None, hostname=hostname)
