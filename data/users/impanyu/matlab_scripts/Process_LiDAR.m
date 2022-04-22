%%--------------------------------------------------------------------------
function ResultsStr3_LiDAR = Process_LiDAR(file_path)
%LiDAR data process
    %Find if the LiDAR raw file exists in the data foler
    LiDARFile = dir(strcat(file_path,'/LiDAR.xls'));
    %fprintf("%s",file_path);
    LiDARStructSize = size(LiDARFile);
        
    %carry out image processing if all image files exist, break if any of them do not exist.   
    if LiDARStructSize(1)==1 
        %read LiDAR raw data and put x, y, and z into the 1st, 2nd, 3rd columns
        [x,y,z] = textread(strcat(file_path,'/LiDAR.xls'),'%f%f%f');
        %define point cloud matrix for pcshow
        xyzPoints = [x,y,z];
        %filter out the xyz not belongs to the target plot (this is an estimated xyz ranges, need
        %double-check by a more accurate method)
        ind_xy = xyzPoints (:,1) > -2 & xyzPoints(:,1) < 2 & xyzPoints(:,2) > -2.5 &...
            xyzPoints(:,2)< 2.5 & xyzPoints(:,3)>0.5;%refer notes for these ranges
        xyzPoints_xy = xyzPoints(ind_xy,:); %use index to get the chosen points
        %canopy height calculation using ground level (Z_max_plot) and 10% percentile of the Z values of
        %the point clouds. Canopy height = Z_max_plot - 10% percentile of all
        Z_max_plot = max(xyzPoints_xy(:,3));
        canopydistance_10pct = prctile(xyzPoints_xy(:,3),10);
        CanopyHeight = Z_max_plot - canopydistance_10pct;
        
        %Save result for output
        ResultsStr3_LiDAR = {num2str(CanopyHeight,'%1.3f')};
    else
        %put 999 into the result array if any file is missing.
        ResultsStr3_LiDAR = {999};
        
    end
end
