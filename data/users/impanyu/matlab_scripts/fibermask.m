%Function: VNIR image processing for fiber FoV
function mask_fiber = fibermask(Xmax, Ymax)
darkmatrix = false(Xmax, Ymax);
    %set value to True if it is within the radius
    Xc = Xmax/2;
    Yc = Ymax/2;

    %pixel count of the FoV radius
    Radius = (Ymax/2) / tand(22.5)*tand(12.5);
    
    for i=1:Xmax
        
        for j=1:Ymax
            if hypot(i-Xc, j-Yc) <= Radius
                darkmatrix(i, j) = true;
            end
            
        end
    end
    
    %mask operation 
    mask_fiber = uint8(darkmatrix);
end