import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime
import gc
gc.collect()
inityear = 1961
eyear = inityear+9
mon = 11
variant = 'r1i1p1f1'
grid = 'gn'
model = 'BCC-CSM2-MR'
path = 'hpchome/nanditha/CMIP6_decadal/BCC-CSM2-MR/tas/tas_Amon_'+model+'_dcppA-hindcast_s'+str(inityear)+'-'+variant+'_'+grid+'_'+str(inityear)+'01-'+str(eyear)+'12.nc'
ds = xr.open_dataset(path)#,client=Client(n_workers=1)

# Each decadal file has simultions for 10 lag periods
# Need to pick same lag year simultion from different datasets

# For convenience global data divided to 7 regions and for each region nc file is created
# need lag0, lag1, lag 5 and lag 9
p= 2 # region number SouthAmerica
variant = 'r1i1p1f1'
grid = 'gn'
regrid_lat = np.arange(-90,90.1,0.1)
regrid_lon = np.arange(0,360,0.1) # excluding 360
lags = (1,5,9)
model = 'BCC-CSM2-MR'
variable = 'tas'
for y in lags:
    # Create a datetime object with the given date
    final = None
    date_ind = 12*y
    for i in range(1961,2015):  
        
        inityear = i
        sinityear = inityear-1
        endyear = inityear+9
        path = 'hpchome/nanditha/CMIP6_decadal/'+model+'/'+variable+'/'+variable+'_Amon_'+model+'_dcppA-hindcast_s'+str(inityear)+'-'+variant+'_'+grid+'_'+str(inityear)+'01-'+str(endyear)+'12.nc'
        ds = xr.open_dataset(path)#,client=Client(n_workers=1)
        ds[variable] = ds[variable].where(ds[variable]>=0,0) # replace values when condition is false, i.e. replace values below zero to 0
        start_date = ds.time[date_ind]
        end_date = ds.time[date_ind+11]

        timeslice = ds.sel(time=slice(start_date, end_date))#.resample(time="M").sum(skipna=True)  # selecting data for a particular lead time from the 10 year initialization data
        ds_regrid =  timeslice.interp(lat=regrid_lat,lon=regrid_lon,method='linear')
        subset = ds_regrid.sel(lon = slice(278,325.5), lat = slice(-56,9.9)) # South.America
        subset[variable].values = subset[variable].values-273.15#*86400 # changing precipitation units to mm
         # Merge the subsets into the final dataset
        if final is None:
            final = subset
        else:
          try:
            final = xr.merge([final,subset])
          except:
            subset = subset.assign_coords(lat_bnds=final.lat_bnds)
            #print((final.lat_bnds-subset.lat_bnds).max())
            subset = subset.set_coords('lat_bnds')
            final = final.set_coords('lat_bnds')
            final = xr.merge([final,subset])
              
        print(i)
   # final['pr'] = final['pr'].where(final['pr']>=0,0) # replace values when condition is false, i.e. replace values below zero to 0
    path2 = 'hpchome/nanditha/CMIP6_decadal/'+model+'/'+variable+'/Regridded_1degree/region'+str(p)+'/'+variable+'_mon_'+model+'_dcppA-hindcast_s1961_lag'+str(y)+'_region'+str(p)+'.nc'
    final.to_netcdf(path2)
    print(f'Lag {y} is completed')
