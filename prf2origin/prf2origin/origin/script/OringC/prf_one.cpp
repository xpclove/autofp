/*------------------------------------------------------------------------------*
 * File Name:				 													*
 * Creation: 																	*
 * Purpose: OriginC Source C file												*
 * Copyright (c) ABCD Corp.	2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010		*
 * All Rights Reserved															*
 * 																				*
 * Modification Log:															*
 *------------------------------------------------------------------------------*/
 
////////////////////////////////////////////////////////////////////////////////////
// Including the system header file Origin.h should be sufficient for most Origin      
// applications and is recommended. Origin.h includes many of the most common system
// header files and is automatically pre-compiled when Origin runs the first time.
// Programs including Origin.h subsequently compile much more quickly as long as
// the size and number of other included header files is minimized. All NAG header
// files are now included in Origin.h and no longer need be separately included.
//
// Right-click on the line below and select 'Open "Origin.h"' to open the Origin.h
// system header file.
#include <Origin.h>
////////////////////////////////////////////////////////////////////////////////////

//#pragma labtalk(0) // to disable OC functions for LT calling.

////////////////////////////////////////////////////////////////////////////////////
// Include your own header files here.


////////////////////////////////////////////////////////////////////////////////////
// Start your functions here.


int test()
{
	printf("hello world! here is Origin 9. ");
	DWORD color=RGB(130,130,0);
	Project.ClearModified(); // Prevent Save As dialog
    Project.Open(); // Open new project

	//WorksheetPage wksPage("Book1");
	
	WorksheetPage wksPage;//("Book1");
	wksPage.Create("../template/PRF.otw");
	
 
	// Add a new sheet to the workbook
	//int index = wksPage.AddLayer("Sheet2"); 
	 
	// Access the new worksheet
	//Worksheet wksNew = wksPage.Layers(index); 
	string str_worksheet="["+wksPage.GetName()+"]"+"./test";
	Worksheet wksNew(str_worksheet);
	
	// Set the new worksheet to be active
	set_active_layer(wksNew);
	
	Worksheet wks=wksPage.Layers(0);
	
	string strFile = "./test.dat"; // some data file name
	ASCIMP	ai;
	if(0 == AscImpReadFileStruct(strFile, &ai) )
	{
		// In this example we will disable the ASCII import progress
		// bar by setting the LabTalk System Variable @NPO to zero.
		// This is optional and is done here to show it is possible.
		// The LTVarTempChange class makes setting and restoring a
		// LabTalk variable easy.  See the Accessing LabTalk section
		// for more details about the LTVarTempChange class.
		LTVarTempChange progressBar("@NPO", 0); // 0 = disable progress bar
	 
		// Get active worksheet from active work book.
		Worksheet wks = Project.ActiveLayer();
	 
		if(0 == wks.ImportASCII(strFile, ai))
			out_str("Import data successful.");
	}
	

	
	DataRange dr;
	dr.Add(wks, 0, "X"); // 1st column for X data
	dr.Add(wks, 1, "Y"); // 2nd column for Y data
	dr.Add(wks, 3, "Y");
	
	GraphPage gp;
	gp.Create("../template/PRF_IMG.otp"); // create a graph using the 3D template
	GraphLayer gl = gp.Layers(); // Get active layer
	
	// Plot XY data range as scatter
	// IDM_PLOT_SCATTER is plot type id, see other types plot id in oPlotIDs.h file.
	int nPlotIndex = gl.AddPlot(wks);
	// Returns plot index (offset is 0), else return -1 for error
	if( nPlotIndex >= 0 ) 
	{
		gl.Rescale(); // Rescale axes to show all data points
	}
		



	return 0;
}