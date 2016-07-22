function postSync() {
  
  // following are production sheets. if you are testing, COMMENT OUT BELOW and UNCOMMENT NEXT
  ipc_schedules = SpreadsheetApp.openById("12Zj8m8eHsiYLdX-EHUY_7jSOHupPjfqWWg225zaiOVI");
  ipc_schedules_history = SpreadsheetApp.openById("16rM8WDAXQTGzaQUOM8d8EhVWTa0t4NpbfuOUsSZ6DuI");
  
  // following are test sheets
  // ipc_schedules = SpreadsheetApp.openById("1BegkkqiaA8TqCQLd2RJkKLLbmmdvFLJ14XkpweEgl28");
  // ipc_schedules_history = SpreadsheetApp.openById("1jB5PAoisKDQMv0SO2P77GCiaZVIejkM2lQyghSftCIM");
  
  sheet_count = ipc_schedules.getNumSheets();  
  
  ipc_schedules.getSheets().forEach(function(sheet) {   
    if (sheet.getName() !== "Reference") {
      last_column = sheet.getLastColumn();
      
      setColumnBackgroundColor(sheet, 10, 211, 252, true);
      
      for (i=1; i <= last_column; i++) {
        sheet.autoResizeColumn(i);
      }

      hideColumn(sheet, 'ID');
      
      statusColumn = getColumnIndex(sheet, "Status");
      
      markCell(sheet, statusColumn, "Cancelled", 199, 149, 179, false);
      
      syncHistory(sheet, ipc_schedules_history, "ID", 110, 218, 28, false);  // hex 6eda1c
    }
  });
  
  moveSheet(ipc_schedules, "Chennai", "TN East");
}


function syncHistory(sheet, history_book, columnName, r, g, b, bold) {
  sourceSheet = sheet;
  sourceSheetName = sheet.getName();
  
  destinationSheet = history_book.getSheetByName(sourceSheetName);
  
  if (destinationSheet === null) {
    lastRow = sourceSheet.getLastRow();
    
    for (i=2; i <= lastRow; i++) {
      colorRange = sourceSheet.getRange(i, 2, 1, 6);
      colorRange.setBackgroundRGB(r, g, b);
      if (bold === true) {
        colorRange.setFontWeight("bold");
      }
    }
    
    newDestinationSheet = sourceSheet.copyTo(history_book);
    newDestinationSheet.setName(sourceSheetName);
    
    return 0;
  }
  
  destinationIDList = getColumnValues(destinationSheet, "ID");
  serialList = getColumnValues(destinationSheet, "SNo");
    
  lastRow = sourceSheet.getLastRow();
  idColumn = getColumnIndex(sourceSheet, "ID");
  
  for (i=2; i <= lastRow; i++) {
    currentID = sourceSheet.getRange(i, idColumn, 1, 1).getDisplayValue();
    colorRange = sourceSheet.getRange(i, 2, 1, 6);
    
    if (destinationIDList.indexOf(currentID) === -1) {
      colorRange.setBackgroundRGB(r, g, b);
      if (bold === true) {
        colorRange.setFontWeight("bold");
      }
      continue;
    }
    
    shadyRange = destinationSheet.getRange(parseInt(serialList[destinationIDList.indexOf(currentID)]) + 1, 2, 1, 1);
    shadyColor = shadyRange.getBackground();
    
    switch (shadyColor) {
      case "#6eda1c":
        destinationColor =  "#eafa0a";
        break;
        
      case "#eafa0a":
        destinationColor = "#d1d58f";
        break;
        
      default:
        destinationColor = "#ffffff";
    }
    
    if (!(destinationColor === "#ffffff")) {
    colorRange.setBackground(destinationColor);
      if (bold) {colorRange.setFontWeight("bold"); }
    }
  }
  
  history_book.deleteSheet(destinationSheet);
  newDestinationSheet = sourceSheet.copyTo(history_book);
  newDestinationSheet.setName(sourceSheetName);

}

function moveSheet(ipc_schedules, source_sheet, before_sheet) {
  src = ipc_schedules.getSheetByName(source_sheet);
  
  bef = ipc_schedules.getSheetByName(before_sheet);
  
  src.activate();
  ipc_schedules.moveActiveSheet(bef.getIndex() - 1);
}

function hideColumn(sheet, columnName) {
  sheet.hideColumns(getColumnIndex(sheet, columnName));
}

function setColumnBackgroundColor(sheet, r, g, b, bold) {
  columns = sheet.getRange(1, 1, 1, sheet.getLastColumn());
  if (bold === true) {
    columns.setFontWeight("bold");}
  columns.setBackgroundRGB(r, g, b);
}

function getColumnIndex(sheet, columnName) { 
  for (i=1; i <= sheet.getLastColumn(); i++) {
    if (sheet.getRange(1, i, 1, 1).getDisplayValue() === columnName) {
      return i;
    }
  }
  
  return 0;
}

function markCell(sheet, column, value, r, g, b, bold) {
  lastRow = sheet.getLastRow();
  
  for (i=1; i <= lastRow; i++)
  {
    currentCell = sheet.getRange(i, column, 1, 1);
    
    if (currentCell.getDisplayValue() === value) {
      currentCell.setBackgroundRGB(r, g, b);
      if (bold === true) {
        columns.setFontWeight("bold");}
    }
  }
  
}

function collapseRange(twoDRange) {
  columnRange = [];
   for (i=0; i < twoDRange.length; i++) {
    if (twoDRange[i][0]) {
        columnRange.push(twoDRange[i][0]);}
  }
  
  return columnRange;
}


function missingSheet() {
  ipc_schedules = SpreadsheetApp.openById("12Zj8m8eHsiYLdX-EHUY_7jSOHupPjfqWWg225zaiOVI");
  
  test = ipc_schedules.getSheetByName("Non Existent");
  
  Logger.log(test);
  Logger.log(test === null);
}

function rangeTest() {
  ipc_schedules = SpreadsheetApp.openById("12Zj8m8eHsiYLdX-EHUY_7jSOHupPjfqWWg225zaiOVI");
  test = ipc_schedules.getSheetByName("Chennai");
  
  myrange = test.getRange("A2");
  Logger.log(myrange.getBackground());
  Logger.log(myrange.getBackground() === "#ffffff");
}

function getColumnValues(sheet, column) {
  columnIndex = getColumnIndex(sheet, column);
  
  valueRange = sheet.getRange(2, columnIndex, sheet.getLastRow() - 1, 1).getDisplayValues();
  return collapseRange(valueRange);  
}