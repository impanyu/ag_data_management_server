function ResultsStr2_ImageProcessing = Process_VNIRThermal(file_path)
%Image processing for RGB, near-infrared, and thermal-infrared images 
    
%Find if RGB, NIR, and thermal image files exist in the data foler
fprintf("%s\n",class(file_path));
RGBFile = dir(convertCharsToStrings(file_path)+"/RGB*.tif"); 
NIRFile = dir(convertCharsToStrings(file_path)+"/NIR*.tif");

IRFile_Vege = dir(convertCharsToStrings(file_path)+"/Infrared_RawPixel_Vege.tiff");
IRFile_Soil = dir(convertCharsToStrings(file_path)+"/Infrared_RawPixel_Soil.tiff");
IRFile_Display = dir(convertCharsToStrings(file_path)+"/Infrared_Display_Vege.tiff");

RGBStructSize = size(RGBFile);
NIRStructSize = size(NIRFile);

IRVegeStructSize = size(IRFile_Vege);
IRSoilStructSize = size(IRFile_Soil);
IRDisplayStructSize = size(IRFile_Display);

%carry out image processing if all image files exist, break if any of them do not exist.   
if RGBStructSize(1)==1 && NIRStructSize(1)==1 && IRVegeStructSize(1)==1 &&...
        IRSoilStructSize(1)==1 && IRDisplayStructSize(1) == 1
    %get the file names
    filename_RGB = RGBFile.name;
    filename_NIR = NIRFile.name;
    filename_IR_Vege = IRFile_Vege.name;
    filename_IR_Soil = IRFile_Soil.name;
    filename_IR_Display = IRFile_Display.name;
    %read NIR raw image
    Image_NIR = imread(convertCharsToStrings(file_path)+"/"+filename_NIR);
    %read RGB raw image
    Image_RGB = imread(convertCharsToStrings(file_path)+"/"+filename_RGB);
    %read IR_Vege image
    Image_IR_Vege = imread(convertCharsToStrings(file_path)+"/"+filename_IR_Vege);
    %read IR_Soil image
    Image_IR_Soil = imread(convertCharsToStrings(file_path)+"/"+filename_IR_Soil);
    %read IR Vege DISPLAY image
    Image_IR_Display = imread(convertCharsToStrings(file_path)+"/"+filename_IR_Display);
    
    %---plant segementation
    %variants in the function
    rgbRaw = Image_RGB;
    nirRaw = Image_NIR;
    %produce NDVI image
    redRaw = rgbRaw(:,:,1);
    c = double(nirRaw-redRaw);
    b = double(nirRaw+redRaw);
    NDVI_Raw = c./b;
    %Segment soil shadow out using NIR image 
    %create binary image from NDVI_raw and use as a mask
    NDVI_Raw_log = NDVI_Raw > 0;
    %Use NIR band alone to do the segementation
    NIR_01 = mat2gray(Image_NIR);
    %use a fixed threshold
    BW_fixed = imbinarize(NIR_01,0.15);
    %segmentation result by multiplying two result images
    Binary_NDVINIR1 = NDVI_Raw_log.*BW_fixed;
    
    %---calculate canopy coverage
    %function variant
    Binary_GPF = Binary_NDVINIR1;
    %define SE for imopen function
    SE = strel('disk',1);        
    Binary_GPF_2 = imopen (Binary_GPF,SE);
    %Canopy Coverage calculation using the FOV of VNIR image
    RawPixelCount = size (Binary_GPF_2);
    CanopyCoverage = sum(uint16(Binary_GPF_2(:)))/RawPixelCount(1)/RawPixelCount(2);
    %output image results
    imwrite(Binary_GPF_2,'SegmentationResult_CanopyCoverage.bmp');
    
    %---image registration 
    %The matrix T was updated for the 45 degree IR lens. 
    T=[0.6154,-0.0108,0; 0.0130,0.6146,0; 8.0367,3.5358,1];
    %convert transformation matrix into the correct type for 'imwarp'
    tform_aff = affine2d(T);  
    %image registration for the segmentation result for RGB and NIR images.
    NDVINIR_registered_aff = imwarp (Binary_NDVINIR1, tform_aff, 'OutputView',...
        imref2d(size(Image_IR_Display))); 
    %imopen for the registerd NDVI image
    BW = NDVINIR_registered_aff;
    SE = strel('disk',1);
    BW2 = imopen (BW,SE);
    %output registered segmentation result
    imwrite(BW2,'SegmentationResult_registered.bmp');
     
    %---average canopy, soil, and plot temperature 
    %Avg canopy temperature calculation
    %change the format for matrix multiply
    Mask_canopy = uint16(BW2);
    CanopyRawPixel = Image_IR_Vege.*Mask_canopy;
    CanopyPixelCount = sum (Mask_canopy(:));
    Canopy_Pixel_Avg = sum(CanopyRawPixel(:))/CanopyPixelCount;
    Canopy_TempC_Avg = Canopy_Pixel_Avg/100-273.15;
           
    %Avg soil/background temperature calculation. 
    %get complement binary image (zero becomes one, one becomes zero)
    Mask_soil = uint16(imcomplement(BW2));
    %figure,imshowpair(RGB_registered_aff,Mask_soil,'montage')
    SoilRawPixel = Image_IR_Soil.*Mask_soil;
    SoilPixelCount = sum (Mask_soil(:));
    Soil_Pixel_Avg = sum(SoilRawPixel(:))/SoilPixelCount;
    Soil_TempC_Avg = Soil_Pixel_Avg/100-273.15;
    
    %Avg temperature needs to be caculated after obtaining the pixel-wise canopy temp,
    %pixel-wise soil temp, plant pixel count in the cropped RGB image.
    Plot_TempC_Avg = ((sum(CanopyRawPixel(:))+ sum(SoilRawPixel(:)))/(480*640))/100-273.15; 
    %calculate canopy coverate rate, average canopy and soil temperature in the FoV of the fiber
    %optic cable
    
    %create the mask, this section needs to be out of the for loop in the main program
    %creat a fiber FoV mask
    mask_VNIR_fiber = fibermask(768, 1024);
    %binary result from crop segementation    
    BW2_beforeregister = imopen(Binary_NDVINIR1, SE);
    Mask_canopy_beforeregister = uint8(BW2_beforeregister);
    %new mask within FoV
    Mask_canopy_Fiber_VNIR = Mask_canopy_beforeregister.*mask_VNIR_fiber;
    %output the mask file
    Mask_canopy_Fiber_logic = logical(Mask_canopy_Fiber_VNIR);
    imwrite(Mask_canopy_Fiber_logic, 'SegmentationResult_VNIR_fiber.bmp')
    %output the masked VNIR images
    Image_RGB_Fiber = Image_RGB .* mask_VNIR_fiber;
    imwrite(Image_RGB_Fiber, 'Cropped_RGB_fiber.bmp')
    Image_RGB_seg_Fiber = Image_RGB .* Mask_canopy_Fiber_VNIR;
    imwrite(Image_RGB_seg_Fiber, 'Cropped_RGB_seg_fiber.bmp')
    
    Image_NIR_Fiber = Image_NIR .* mask_VNIR_fiber;
    imwrite(Image_NIR_Fiber, 'Cropped_NIR_fiber.bmp')
    Image_NIR_seg_Fiber = Image_NIR .* Mask_canopy_Fiber_VNIR;
    imwrite(Image_NIR_seg_Fiber, 'Cropped_NIR_seg_fiber.bmp')
    
    %calculate canopy coverage rate in the fiber FoV
    plantpixelcount_Fiber = sum(Mask_canopy_Fiber_VNIR(:));
    CanopyCoverage_Fiber = plantpixelcount_Fiber / sum(mask_VNIR_fiber(:));
    %-------------------------------------------
    %calculate canopy and soil temperature in the fiber FoV
    %creat a fiber FoV mask
    mask_IR_fiber = fibermask(480, 640);
    %new mask within FoV
    Mask_canopy_Fiber_IR = BW2 .* double(mask_IR_fiber);
    Mask_canopy_Fiber_IR_logic = logical(Mask_canopy_Fiber_IR);
    imwrite(Mask_canopy_Fiber_IR_logic, 'SegmentationResult_IR_fiber.bmp')
  
    %canopy temperature within fiber FoV
    Mask_canopy_Fiber = uint16(Mask_canopy_Fiber_IR);
    CanopyRawPixel_Fiber = Image_IR_Vege .* Mask_canopy_Fiber;
    imwrite(double(CanopyRawPixel_Fiber), 'Cropped_IR_fiber.bmp');
    CanopyPixelCount_Fiber = sum (Mask_canopy_Fiber(:));
    Canopy_Pixel_Fiber_Avg = sum(CanopyRawPixel_Fiber(:))/CanopyPixelCount_Fiber;
    Canopy_TempC_Fiber_Avg = Canopy_Pixel_Fiber_Avg/100-273.15;
    %soil temperature within fiber FoV
    Mask_soil_Fiber = uint16(imcomplement(Mask_canopy_Fiber_IR));
    %figure,imshowpair(RGB_registered_aff,Mask_soil,'montage')
    SoilRawPixel_Fiber = Image_IR_Soil.*Mask_soil_Fiber;
    SoilPixelCount_Fiber = sum (Mask_soil_Fiber(:));
    Soil_Pixel_Fiber_Avg = sum(SoilRawPixel_Fiber(:))/SoilPixelCount_Fiber;
    Soil_TempC_Fiber_Avg = Soil_Pixel_Fiber_Avg/100-273.15;
    %plot average temperature within fiber FoV
    Plot_TempC_Fiber_Avg = ((sum(CanopyRawPixel_Fiber(:))+ sum(SoilRawPixel_Fiber(:)))/(480*640))/100-273.15;  
                
    %%Save result for output
    ResultsStr2_ImageProcessing = {num2str(CanopyCoverage,'%1.3f'), num2str(Plot_TempC_Avg,'%2.2f'),...
        num2str(Canopy_TempC_Avg,'%2.2f'),num2str(Soil_TempC_Avg,'%2.2f'),...
        num2str(CanopyCoverage_Fiber,'%1.3f'), num2str(Plot_TempC_Fiber_Avg,'%2.2f'),...
        num2str(Canopy_TempC_Fiber_Avg,'%2.2f'),num2str(Soil_TempC_Fiber_Avg,'%2.2f')};
      
else
    %put 999 into the result array if any file is missing.
    ResultsStr2_ImageProcessing = zeros(1,8) + 999;
    ResultsStr2_ImageProcessing = num2cell(ResultsStr2_ImageProcessing);
end
end
