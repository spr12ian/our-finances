const Sheet = class {
  constructor(spreadsheet) {
    this.spreadsheet = spreadsheet;
    this.spreadsheetName = spreadsheet.getName();
    console.log(`Spreadsheet: ${this.spreadsheetName}`);
  }

  getRange(range) {
    return this.spreadsheet.getRange(range);
  }

  getValue(range) {
    return this.getRange(range).getValue();
  }

  setValue(range, value) {
    return this.getRange(range).setValue(value);
  }
}

const AccountSheet = class extends Sheet {
  static get COL_BALANCE() { return 8; }
  static get COL_COUNTERPARTY() { return 6; }
  static get COL_COUNTERPARTY_DATE() { return 7; }
  static get COL_CREDIT() { return 3; }
  static get COL_DATE() { return 1; }
  static get COL_DEBIT() { return 4; }
  static get COL_DESCRIPTION() { return 2; }
  static get COL_NOTE() { return 5; }

  static get HEADERS() {
    return [
      'Date',
      'Description',
      'Credit',
      'Debit',
      'Note',
      'CPTY',
      'CPTY Date',
      'Balance',
    ];
  }

  static get MINIMUM_COLUMNS() { return 8; }

  constructor(sheet) {
    const spreadsheet = sheet.getParent();
    super(spreadsheet);
    this.sheet = sheet;
    this.sheetName = sheet.getName();
    this.log(`AccountSheet initialized for sheet: ${this.sheetName}`);
  }

  addDefaultNotes() {
    this.addNoteToCell('F1', 'Counterparty');
    this.addNoteToCell('G1', 'Counterparty date');
  }

  addNoteToCell(a1CellRange, note) {
    this.sheet.getRange(a1CellRange).setNote(note);
    this.log(`Added note '${note}' to cell ${a1CellRange}`);
  }

  alignLeft(a1range) {
    this.sheet.getRange(a1range).setHorizontalAlignment('left');
    this.log(`Aligned range ${a1range} to the left`);
  }

  analyzeSheet() {
    this.log('Starting sheet analysis');

    try {
      this.logSheetDetails();
      this.validateSheet();
      this.setSheetFormatting();
      this.addDefaultNotes();
      this.convertColumnToUppercase(AccountSheet.COL_DESCRIPTION);
      this.convertColumnToUppercase(AccountSheet.COL_NOTE);
      this.setColumnWidth(AccountSheet.COL_DESCRIPTION, 500);
      this.setColumnWidth(AccountSheet.COL_NOTE, 170);
    } catch (error) {
      this.log(`Error during sheet analysis: ${error.message}`, 'error');
      throw error;
    }

    this.log('Sheet analysis completed successfully');
  }

  convertColumnToUppercase(column) {
    const START_ROW = 2;
    const sheet = this.sheet;

    const lastRow = sheet.getLastRow();
    const numRows = lastRow + 1 - START_ROW;

    const range = sheet.getRange(START_ROW, column, numRows, 1);
    const values = range.getValues();
    const uppercasedValues = values.map(row => [row[0].toString().toUpperCase()]);

    range.setValues(uppercasedValues);
  }

  formatAsBold(a1range) {
    this.sheet.getRange(a1range).setFontWeight('bold');
    this.log(`Set range ${a1range} to bold`);
  }

  formatAsDate(...a1ranges) {
    a1ranges.forEach(a1range => {
      this.setNumberFormat(a1range, 'dd/MM/yyyy');
      this.setDateValidation(a1range);
    });
  }

  formatAsUKCurrency(...a1ranges) {
    a1ranges.forEach(a1range => {
      this.setNumberFormat(a1range, '£#,##0.00');
      this.setConditionalCcyFormattingByValue(a1range);
    });
  }

  getExpectedHeader(column) {
    if (column === AccountSheet.COL_DESCRIPTION) {
      const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
      const bankAccountSheet = spreadsheet.getSheetByName('Bank accounts');
      const key = this.sheetName.slice(1);
      return this.xLookup(key, bankAccountSheet, 'A', 'AQ');
    } else {
      return AccountSheet.HEADERS[column - 1];
    }
  }

  log(message, level = 'info') {
    const logPrefix = `[${this.sheetName}] `;
    const logMessage = `${logPrefix}${message}`;
    level === 'error' ? console.log(`ERROR: ${logMessage}`) : console.log(logMessage);
  }

  logSheetDetails() {
    const lastColumn = this.sheet.getLastColumn();
    this.log(`Logging sheet details...`);
    this.log(`Minimum required columns: ${AccountSheet.MINIMUM_COLUMNS}`);
    this.log(`Sheet name: ${this.sheetName}`);
    this.log(`Last column with data: ${lastColumn}`);
    this.log(`Maximum possible columns: ${this.sheet.getMaxColumns()}`);
  }

  setBackground(a1range, background = '#FFFFFF') {
    const range = this.sheet.getRange(a1range);
    // Validate and apply background color if provided
    if (background) {
      range.setBackground(background);
      this.log(`Background color set to ${background}`);
    }

    this.log(`Completed setting font and background for the entire sheet`);
  }

  setColumnWidth(column, widthInPixels) {
    // Set the width of column to widthInPixels
    this.sheet.setColumnWidth(column, widthInPixels);
  }

  setConditionalCcyFormattingByValue(a1range) {
    const sheet = this.sheet;
    const range = sheet.getRange(a1range);

    // Create a new conditional format rule
    const rule = SpreadsheetApp.newConditionalFormatRule()
      .whenNumberLessThan(0) // Condition: when the cell value is less than zero
      .setFontColor("#FF0000") // Set the font color to red
      .setRanges([range]) // Apply the rule to the specified range
      .build();

    // Get the current rules
    const rules = sheet.getConditionalFormatRules();

    // Add the new rule to the list of rules
    rules.push(rule);

    // Apply all rules to the sheet
    sheet.setConditionalFormatRules(rules);

    this.log(`Set font colour to red for ${a1range} where value < zero`);
  }

  setCounterpartyValidation(a1range) {
    const sheet = this.sheet;
    const spreadsheet = this.spreadsheet;
    const range = sheet.getRange(a1range);

    // Create the data validation rule
    const rule = SpreadsheetApp.newDataValidation()
      .setAllowInvalid(false)
      .requireValueInRange(spreadsheet.getRange('\'Bank accounts\'!$A$2:$A'), true)
      .setHelpText('Please select a valid counterparty.') // Set the help text
      .build();

    // Apply the validation rule to the range
    range.setDataValidation(rule);
  }

  setDateValidation(a1range) {
    const sheet = this.sheet;
    const range = sheet.getRange(a1range);

    // Create the data validation rule
    const rule = SpreadsheetApp.newDataValidation()
      .requireDate()
      .setAllowInvalid(false)
      .setHelpText('Please enter a valid date in the format DD/MM/YYYY.') // Set the help text
      .build();

    // Apply the validation rule to the range
    range.setDataValidation(rule);
  }

  setNumberFormat(a1range, format) {
    this.sheet.getRange(a1range).setNumberFormat(format);
    this.log(`Set number format for ${a1range} to '${format}'`);
  }

  setSheetFont(fontFamily = 'Arial', fontSize = 10, fontColor = '#000000') {
    // Get the data range of the entire sheet
    const range = this.sheet.getDataRange();

    // Validate and apply font family if provided
    if (fontFamily) {
      range.setFontFamily(fontFamily);
      this.log(`Font family set to ${fontFamily}`);
    }

    // Validate and apply font size if provided
    if (fontSize && typeof fontSize === 'number') {
      range.setFontSize(fontSize);
      this.log(`Font size set to ${fontSize}`);
    }

    // Validate and apply font color if provided
    if (fontColor) {
      range.setFontColor(fontColor);
      this.log(`Font color set to ${fontColor}`);
    }

    this.log(`Completed setting font and background for the entire sheet`);
  }

  setSheetFormatting() {
    // Clear all conditional format rules
    this.sheet.setConditionalFormatRules([]);

    // Clear all data validation rules
    this.sheet.getDataRange().clearDataValidations();

    this.setCounterpartyValidation('F2:F');

    this.setSheetFont();
    this.formatAsDate('A2:A', 'G2:G');
    this.formatAsUKCurrency('C2:D', 'H2:H');
    this.formatAsBold('A1:H1');
    this.alignLeft('A1:H1');
    this.setBackground('A1:H1');
  }

  validateFrozenRows() {
    this.log(`Validating frozen rows`);

    const frozenRows = this.sheet.getFrozenRows();
    this.log(`frozenRows: ${frozenRows}`);

    if (frozenRows !== 1) {
      throw new Error(`There should be only one frozen row; found ${frozenRows}`);
    }

    this.log('Frozen rows validation passed');
  }

  validateHeaders() {
    this.log('Validating headers');
    const headers = this.sheet.getRange(1, 1, 1, AccountSheet.MINIMUM_COLUMNS).getValues()[0];

    headers.forEach((value, index) => {
      const expected = this.getExpectedHeader(index + 1);
      if (value !== expected) {
        throw new Error(`Column ${index + 1} should be '${expected}' but found '${value}'`);
      }
    });

    this.log('Headers validation passed');
  }

  validateMinimumColumns() {
    const lastColumn = this.sheet.getLastColumn();

    if (lastColumn < AccountSheet.MINIMUM_COLUMNS) {
      throw new Error(`Sheet ${this.sheetName} should have at least ${AccountSheet.MINIMUM_COLUMNS} columns, but only found ${lastColumn}`);
    }

    this.log('Minimum columns validation passed');
  }

  validateSheet() {
    this.log('Starting sheet validation');
    this.validateMinimumColumns();
    this.validateHeaders();
    this.validateFrozenRows();
    this.log('Sheet validation completed');
  }

  xLookup(searchValue, sheet, searchCol, resultCol) {
    const searchRange = sheet.getRange(`${searchCol}1:${searchCol}`).getValues();

    for (let i = 0; i < searchRange.length; i++) {
      if (searchRange[i][0] === searchValue) {
        return sheet.getRange(`${resultCol}${i + 1}`).getValue();
      }
    }

    this.log(`Value '${searchValue}' not found in column ${searchCol}`);
    return null;
  }
}

const BalanceSheet = class {
  static get SHEET_NAME() { return 'Balance Sheet'; }
  constructor(spreadsheet) {
    this.sheetName = BalanceSheet.SHEET_NAME;
    this.spreadsheet = spreadsheet;
    this.sheet = spreadsheet.getSheetByName(this.sheetName);

    if (!this.sheet) {
      throw new Error(`Sheet '${this.sheetName}' not found.`);
    }

    this.log(`Initialized sheet: ${this.sheetName}`);
  }

  getSheetName() {
    return this.sheetName;
  }

  getSheet() {
    return this.sheet;
  }

  log(message, level = 'info') {
    const logPrefix = `[${this.sheetName}] `;
    const logMessage = `${logPrefix}${message}`;
    level === 'error' ? console.log(`ERROR: ${logMessage}`) : console.log(logMessage);
  }
}

const Spreadsheet = class {
  constructor(spreadsheetId) {
    if (spreadsheetId) {
      this.spreadsheet = SpreadsheetApp.openById(spreadsheetId);
    } else {
      this.spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    }
  }

  getRangeByName(rangeName) {
    return this.spreadsheet.getRangeByName(rangeName)
  }

  getSheetByName(sheetName) {
    return this.spreadsheet.getSheetByName(sheetName);
  }

  getUrl() {
    return this.spreadsheet.getUrl()
  }
}

const BankAccounts = class {
  static get COL_CHECK_BALANCE_FREQUENCY() { return 12; }
  static get COL_OWNER_CODE() { return 3; }
  static get OWNER_CODE_BRIAN() { return 'A'; }
  static get OWNER_CODE_CHARLIE() { return 'C'; }
  static get OWNER_CODE_LINDA() { return 'L'; }
  static get SHEET_NAME() { return 'Bank accounts'; }

  constructor(ourFinances) {
    this.sheetName = BankAccounts.SHEET_NAME;
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName);

    if (!this.sheet) {
      throw new Error(`Sheet '${this.sheetName}' not found.`);
    }

    this.log(`Initialized sheet: ${this.sheetName}`);
  }

  applyFilters(filters) {
    const sheet = this.sheet;

    // Clear any existing filters
    this.removeFilter();

    const filter = sheet.getDataRange().createFilter();

    filters.forEach(item => {
      const criteria = item.hideValues === null
        ? SpreadsheetApp.newFilterCriteria().whenCellEmpty().build()
        : SpreadsheetApp.newFilterCriteria().setHiddenValues(item.hideValues).build();

      filter.setColumnFilterCriteria(item.column, criteria);
    });

    this.log(`Filters applied: ${JSON.stringify(filters)}`);
  }

  getDataRange() {
    return this.sheet.getDataRange();
  }

  getSheetName() {
    return this.sheetName;
  }

  getSheet() {
    return this.sheet;
  }

  getValues() {
    this.log("Retrieving all values from data range");
    return this.getDataRange().getValues();
  }

  hideColumns(columnsToHide) {
    const sheet = this.sheet;
    const ranges = sheet.getRangeList(columnsToHide);

    ranges.getRanges().forEach(range => sheet.hideColumn(range));
    this.log(`Columns hidden: ${columnsToHide}`);
  }

  log(message, level = 'info') {
    const logPrefix = `[${this.sheetName}] `;
    const logMessage = `${logPrefix}${message}`;
    level === 'error' ? console.log(`ERROR: ${logMessage}`) : console.log(logMessage);
  }


  removeFilter() {
    const sheet = this.sheet;
    const existingFilter = sheet.getFilter();
    if (existingFilter) {
      existingFilter.remove();
    }
    return sheet;
  }

  showAll() {
    const sheet = this.sheet;

    this.removeFilter();
    sheet.showColumns(1, sheet.getLastColumn());
    sheet.setActiveCell(sheet.getRange("B1"));

    this.log("All columns shown and active cell set to B1");
  }

  showDaily() {
    this.showAll();
    const colCheckBalanceFrequency = BankAccounts.COL_CHECK_BALANCE_FREQUENCY;
    const colOwnerCode = BankAccounts.COL_OWNER_CODE;
    const hideOwnerCodes = [
      BankAccounts.OWNER_CODE_BRIAN,
      BankAccounts.OWNER_CODE_CHARLIE,
      BankAccounts.OWNER_CODE_LINDA,
    ];
    const filters = [
      { column: colOwnerCode, hideValues: hideOwnerCodes },
      { column: colCheckBalanceFrequency, hideValues: ["Monthly", "Never"] }
    ];

    this.applyFilters(filters);

    const columnsToHide = ['C:L', 'N:O', 'Q:Q', 'S:AN'];
    this.hideColumns(columnsToHide);
  }

  showMonthly() {
    this.showAll();
    const filters = [
      { column: 3, hideValues: ["C", "L"] },  // Filter by Owner Code (Column C)
      { column: 12, hideValues: ["Daily", "Never"] }  // Filter by Check Balance Frequency (Column L)
    ];

    this.applyFilters(filters);

    const columnsToHide = ['C:L', 'N:O', 'Q:Q', 'S:U', 'W:AJ'];
    this.hideColumns(columnsToHide);
  }

  showOpenAccounts() {
    this.showAll();
    const filters = [
      { column: 3, hideValues: ["C", "L"] },  // Filter by Owner Code (Column C)
      { column: 11, hideValues: null }  // Filter by Date Closed (Column K)
    ];

    this.applyFilters(filters);
  }
}

const BankDebitsDue = class {
  static get COL_ACCOUNT_KEY() { return 0; }
  static get COL_CHANGE_AMOUNT() { return 1; }

  constructor(ourFinances) {
    this.sheetName = 'Bank debits due';
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName);
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    // Check if the sheet exists
    if (!this.sheet) {
      throw new Error(`Sheet "${this.sheetName}" not found in the spreadsheet.`);
    }
  }

  getScheduledTransactions() {
    return this.sheet.getDataRange().getValues();
  }

  getUpcomingDebits() {
    let upcomingPayments = `Due in the next ${this.howManyDaysAhead} days:`

    const scheduledTransactions = this.getScheduledTransactions()

    // Filter and format valid upcoming debits
    scheduledTransactions.forEach(transaction => {
      const accountKey = transaction[BankDebitsDue.COL_ACCOUNT_KEY]?.trim();  // Optional chaining and trim
      const changeAmount = transaction[BankDebitsDue.COL_CHANGE_AMOUNT];

      if (accountKey && Math.abs(changeAmount) > 1) {
        upcomingPayments += `\n\t${accountKey} ${getAmountAsGBP(changeAmount)}`;
      }
    });

    return upcomingPayments
  }
}

const BudgetAnnualTransactions = class {
  static get COL_DATE() { return 0; }
  static get COL_CHANGE_AMOUNT() { return 3; }
  static get COL_DESCRIPTION() { return 1; }
  static get COL_FROM_ACCOUNT() { return 4; }
  static get COL_PAYMENT_TYPE() { return 5; }

  constructor(ourFinances) {
    this.sheetName = 'Budget annual transactions';
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName);
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    if (!this.sheet) {
      throw new Error(`Sheet "${this.sheetName}" not found.`);
    }
  }

  // Get all scheduled transactions from the sheet
  getScheduledTransactions() {
    return this.sheet.getDataRange().getValues();
  }

  // Main method to get upcoming debits
  getUpcomingDebits() {
    console.log('BudgetAnnualTransactions:getUpcomingDebits');
    const howManyDaysAhead = this.howManyDaysAhead;
    const today = getNewDate();
    let upcomingPayments = '';

    // Fetch scheduled transactions and remove the header row
    const scheduledTransactions = this.getScheduledTransactions();
    scheduledTransactions.shift(); // Remove header row

    if (!scheduledTransactions.length) return upcomingPayments;

    // Iterate over each transaction and filter the valid ones
    scheduledTransactions.forEach(transaction => {
      const {
        [BudgetAnnualTransactions.COL_DATE]: date,
        [BudgetAnnualTransactions.COL_CHANGE_AMOUNT]: changeAmount,
        [BudgetAnnualTransactions.COL_DESCRIPTION]: description,
        [BudgetAnnualTransactions.COL_FROM_ACCOUNT]: fromAccount,
        [BudgetAnnualTransactions.COL_PAYMENT_TYPE]: paymentType
      } = transaction;

      if (Math.abs(changeAmount) > 1) {
        const formattedDaySelected = getFormattedDate(new Date(date), "GMT+1", "dd/MM/yyyy");

        // Generate payment details if the date falls within the upcoming days
        const paymentDetails = this._generatePaymentDetails(formattedDaySelected, changeAmount, fromAccount, paymentType, description, today, howManyDaysAhead);
        if (paymentDetails) {
          upcomingPayments += paymentDetails;
        }
      }
    });

    if (upcomingPayments.length) {
      upcomingPayments = '\nAnnual payment(s) due:\n' + upcomingPayments;
    }

    return upcomingPayments;
  }

  // Helper method to generate payment details
  _generatePaymentDetails(formattedDaySelected, changeAmount, fromAccount, paymentType, description, today, howManyDaysAhead) {
    const { first, iterator: days } = setupDaysIterator(today);
    let day = first;

    for (let index = 0; index <= howManyDaysAhead; index++) {
      if (formattedDaySelected === day.day) {
        return `\t${getOrdinalDate(day.date)} ${getAmountAsGBP(changeAmount)} from ${fromAccount} by ${paymentType} ${description}\n`;
      }
      day = days.next();
    }

    return null;
  }
}

const BudgetMonthlyTransactions = class {
  static get COL_DATE() { return 0; }
  static get COL_DEBIT_AMOUNT() { return 3; }
  static get COL_DESCRIPTION() { return 1; }
  static get COL_FROM_ACCOUNT() { return 6; }
  static get COL_PAYMENT_TYPE() { return 9; }

  constructor(ourFinances) {
    this.sheetName = 'Budget monthly transactions'
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName)
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    if (!this.sheet) {
      throw new Error(`Sheet "${this.sheetName}" not found.`);
    }
  }

  getScheduledTransactions() {
    return this.sheet.getDataRange().getValues()
  }

  getUpcomingDebits() {
    const howManyDaysAhead = this.howManyDaysAhead

    let upcomingPayments = ''
    const today = getNewDate()

    const scheduledTransactions = this.getScheduledTransactions()

    // Remove the header row
    scheduledTransactions.shift()

    if (scheduledTransactions.length > 0) {
      upcomingPayments += `\nMonthly payment due:\n`;
      // Get the dates for the upcoming days
      const upcomingDays = [];
      const { first, iterator: days } = setupDaysIterator(today);
      let day = first;
      for (let index = 0; index <= howManyDaysAhead; index++) {
        upcomingDays.push(day);
        day = days.next();
      }

      scheduledTransactions.forEach(transaction => {
        if (Math.abs(transaction[BudgetMonthlyTransactions.COL_DEBIT_AMOUNT]) > 1) {
          const transactionDate = new Date(transaction[BudgetMonthlyTransactions.COL_DATE]);

          upcomingDays.forEach(day => {
            if (transactionDate.toDateString() === day.date.toDateString()) {
              upcomingPayments += `\t${getOrdinalDate(day.date)} `;
              upcomingPayments += `${getAmountAsGBP(transaction[BudgetMonthlyTransactions.COL_DEBIT_AMOUNT])} from `;
              upcomingPayments += `${transaction[BudgetMonthlyTransactions.COL_FROM_ACCOUNT]} by ${transaction[BudgetMonthlyTransactions.COL_PAYMENT_TYPE]} `;
              upcomingPayments += `${transaction[BudgetMonthlyTransactions.COL_DESCRIPTION]}\n`;
            }
          });
        }
      });
    }

    return upcomingPayments
  }
}

const BudgetOneOffTransactions = class {
  static get COL_CHANGE_AMOUNT() { return 3; }
  static get COL_DATE() { return 0; }
  static get COL_DESCRIPTION() { return 1; }
  static get COL_FROM_ACCOUNT() { return 6; }
  static get COL_PAYMENT_TYPE() { return 7; }

  constructor(ourFinances) {
    this.sheetName = 'Budget one-off transactions';
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName);
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    if (!this.sheet) {
      throw new Error(`Sheet "${this.sheetName}" not found.`);
    }
  }

  // Get all transactions from the sheet
  getScheduledTransactions() {
    return this.sheet.getDataRange().getValues();
  }

  // Main method to get upcoming debits
  getUpcomingDebits() {
    let upcomingPayments = '';

    // Fetch scheduled transactions and remove the header row
    const scheduledTransactions = this.getScheduledTransactions();
    scheduledTransactions.shift(); // Remove header row

    if (!scheduledTransactions.length) return upcomingPayments;

    upcomingPayments += '\nOne-off payment(s) due:\n';

    // Iterate over transactions and filter valid ones
    scheduledTransactions.forEach(transaction => {
      const changeAmount = transaction[BudgetOneOffTransactions.COL_CHANGE_AMOUNT];
      const transactionDate = transaction[BudgetOneOffTransactions.COL_DATE];

      if (Math.abs(changeAmount) > 1) {
        const formattedDaySelected = getFormattedDate(new Date(transactionDate), "GMT+1", "dd/MM/yyyy");

        // Use a helper function for better readability
        const upcomingPayment = this._getPaymentDetails(formattedDaySelected, changeAmount, transaction);
        if (upcomingPayment) {
          upcomingPayments += upcomingPayment;
        }
      }
    });

    return upcomingPayments;
  }

  // Helper function to generate payment details
  _getPaymentDetails(formattedDaySelected, changeAmount, transaction) {
    const { first, iterator: days } = setupDaysIterator(getNewDate());
    let day = first;

    for (let index = 0; index <= this.howManyDaysAhead; index++) {
      if (formattedDaySelected === day.day) {
        // Generate payment detail string
        return `\t${getOrdinalDate(day.date)} ${getAmountAsGBP(changeAmount)} from ${transaction[BudgetOneOffTransactions.COL_FROM_ACCOUNT]} by ${transaction[BudgetOneOffTransactions.COL_PAYMENT_TYPE]} ${transaction[BudgetOneOffTransactions.COL_DESCRIPTION]}\n`;
      }
      day = days.next();
    }

    return null;
  }
}

const BudgetWeeklyTransactions = class {
  static get COL_DATE() { return 0; }
  static get COL_DEBIT_AMOUNT() { return 3; }
  static get COL_DESCRIPTION() { return 1; }
  static get COL_FROM_ACCOUNT() { return 6; }
  static get COL_PAYMENT_TYPE() { return 15; }

  constructor(ourFinances) {
    this.sheetName = 'Budget weekly transactions'
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName)
    this.howManyDaysAhead = ourFinances.howManyDaysAhead
  }

  getScheduledTransactions() {
    return this.sheet.getDataRange().getValues()
  }

  getUpcomingDebits() {
    const howManyDaysAhead = this.howManyDaysAhead

    let upcomingPayments = ''
    const today = getNewDate();

    const scheduledTransactions = this.getScheduledTransactions();

    // Lose the header row
    scheduledTransactions.shift();

    scheduledTransactions.forEach(transaction => {
      if (Math.abs(transaction[BudgetWeeklyTransactions.COL_DEBIT_AMOUNT]) > 1) {
        const daySelected = transaction[BudgetWeeklyTransactions.COL_DATE]
        console.log(`daySelected: ${daySelected}`)

        const formattedDaySelected = getFormattedDate(new Date(daySelected), "GMT+1", "dd/MM/yyyy")
        console.log(`formattedDaySelected: ${formattedDaySelected}`)

        // Reset the day iterator
        const { first, iterator: days } = setupDaysIterator(today)
        let day = first
        for (let index = 0; index <= howManyDaysAhead; index++) {
          const dayDay = day.day;

          if (formattedDaySelected === dayDay) {
            upcomingPayments += `\t${getOrdinalDate(day.date)}`
            upcomingPayments += ` ${getAmountAsGBP(transaction[BudgetWeeklyTransactions.COL_DEBIT_AMOUNT])}`
            upcomingPayments += ` from`
            upcomingPayments += ` ${transaction[BudgetWeeklyTransactions.COL_FROM_ACCOUNT]}`
            upcomingPayments += ` by ${transaction[BudgetWeeklyTransactions.COL_PAYMENT_TYPE]}`
            upcomingPayments += ` ${transaction[BudgetWeeklyTransactions.COL_DESCRIPTION]}\n`
          }
          day = days.next()
        }
      }
    })

    if (upcomingPayments.length) {
      upcomingPayments = `\nWeekly payment due:\n${upcomingPayments}`;
    }

    return upcomingPayments
  }
}

const CheckFixedAmounts = class {
  static get COL_DESCRIPTION() { return 0; }
  static get COL_DYNAMIC_AMOUNT() { return 2; }
  static get COL_FIXED_AMOUNT() { return 1; }
  static get COL_MISMATCH() { return 4; }
  constructor(ourFinances) {
    this.sheetName = 'Check Fixed Amounts'
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName)
  }

  getValues() {
    return this.sheet.getDataRange().getValues()
  }

  reportMismatches() {
    const values = this.getValues()

    values.forEach(row => {
      if (row[CheckFixedAmounts.COL_MISMATCH] == 'Mismatch') {
        const mismatchMessage = `${row[CheckFixedAmounts.COL_DESCRIPTION]}: Dynamic amount (${row[CheckFixedAmounts.COL_DYNAMIC_AMOUNT]}) does not match fixed amount (${row[CheckFixedAmounts.COL_FIXED_AMOUNT]})`
        alert(mismatchMessage)
      }
    })
  }
}

const Dependencies = class {
  constructor(spreadsheet) {
    this.sheetName = 'Dependencies'
    this.spreadsheet = spreadsheet
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName)
  }

  getAllDependencies() {
    console.log("Dependencies.getAllDependencies")
    let allDependencies
    const typeofThisAllDependencies = typeof this.allDependencies
    if (typeofThisAllDependencies === 'undefined') {
      allDependencies = this.getSheet().getDataRange().getValues();
      allDependencies.shift();
      this.allDependencies = allDependencies;
    } else {
      allDependencies = this.allDependencies;
    }
    console.log("getAllDependencies: allDependencies %s", allDependencies);
    console.log("getAllDependencies: this.allDependencies %s", this.allDependencies);
    return allDependencies;
  }

  getSheetName() {
    return this.sheetName
  }

  getSpreadsheetNameById(id) {
    try {
      const spreadsheet = SpreadsheetApp.openById(id);
      return spreadsheet.getName();
    } catch (error) {
      console.log(`Error fetching spreadsheet with ID: ${id}. ${error.message}`);
      return null;  // or handle it accordingly
    }
  }

  getSheet() {
    return this.sheet;
  }

  /**
 * Updates the spreadsheet names for all dependencies in the specified column.
 */
  updateAllDependencies() {
    const allDependencies = this.getAllDependencies();
    const col = "B";
    const sheet = this.getSheet();
    const len = allDependencies.length;

    for (let index = 0; index < len; index++) {
      const spreadsheetId = allDependencies[index][0];
      const spreadsheetName = this.getSpreadsheetNameById(spreadsheetId);
      const row = index + 2;
      const a1Notation = col + row;
      const cell = sheet.getRange(a1Notation);
      cell.setValue(spreadsheetName);
    }
  }
}

const OurFinances = class {
  constructor() {
    this.spreadsheet = new Spreadsheet();
  }

  checkFixedAmounts() {
    const checkFixedAmounts = new CheckFixedAmounts(this)
    checkFixedAmounts.reportMismatches()
  }

  emailUpcomingPayments() {
    const subject = `Our Finances: Upcoming debits ${getToday()}`;
    console.log(`Subject: ${subject}`);

    // Initialize the email body
    let emailBody = `${subject}\n`;

    // Collect upcoming debits from different sources
    const upcomingDebits = [
      this.bankDebitsDue.getUpcomingDebits(),
      this.budgetOneOffTransactions.getUpcomingDebits(),
      this.budgetAnnualTransactions.getUpcomingDebits(),
      this.budgetMonthlyTransactions.getUpcomingDebits(),
      this.budgetWeeklyTransactions.getUpcomingDebits()
    ];

    // Concatenate the debits into the email body
    emailBody += upcomingDebits.join("\n");

    console.log(`Email Body: ${emailBody}`);

    // Append the spreadsheet URL
    emailBody += `\n\nSent from (onDateChange): ${this.spreadsheet.getUrl()}\n`;

    // Send the email
    sendMeEmail(subject, emailBody);
  }

  get budgetAnnualTransactions() {
    if (typeof this._budgetAnnualTransactions === 'undefined') {
      this._budgetAnnualTransactions = new BudgetAnnualTransactions(this)
    }
    return this._budgetAnnualTransactions
  }

  get budgetOneOffTransactions() {
    if (typeof this._budgetOneOffTransactions === 'undefined') {
      this._budgetOneOffTransactions = new BudgetOneOffTransactions(this)
    }
    return this._budgetOneOffTransactions
  }

  get bankAccounts() {
    if (typeof this._bankAccounts === 'undefined') {
      this._bankAccounts = new BankAccounts(this)
    }
    return this._bankAccounts
  }

  get bankDebitsDue() {
    if (typeof this._bankDebitsDue === 'undefined') {
      this._bankDebitsDue = new BankDebitsDue(this)
    }
    return this._bankDebitsDue
  }

  get howManyDaysAhead() {
    const _howManyDaysAhead = this.spreadsheet.getRangeByName('LOOK_AHEAD').getValue()
    return _howManyDaysAhead
  }

  get budgetMonthlyTransactions() {
    if (typeof this._budgetMonthlyTransactions === 'undefined') {
      this._budgetMonthlyTransactions = new BudgetMonthlyTransactions(this)
      console.log(`this._budgetMonthlyTransactions.sheetName: ${this._budgetMonthlyTransactions.sheetName}`)
    }
    return this._budgetMonthlyTransactions
  }

  get budgetWeeklyTransactions() {
    if (typeof this._budgetWeeklyTransactions === 'undefined') {
      this._budgetWeeklyTransactions = new BudgetWeeklyTransactions(this)
    }
    return this._budgetWeeklyTransactions
  }

  getName() {
    return this.spreadsheet.getName()
  }

  /*
  This would put whatever "rangeName" is defined as into the cell.
  It will NOT update when you redefine "rangeName," because of GAS's aggressive caching. 
  You can, however, force GAS to update it on every sheet calculation.
  
  =getRangeByName("rangeName",now())
  */
  getRangeByName(rangeName) {
    return this.spreadsheet.getRangeByName(rangeName).getA1Notation();
  }

  getSheetByName(sheetName, logIt) {
    return this.spreadsheet.getSheetByName(sheetName, logIt)
  }

  showAllAccounts() {
    this.bankAccounts.showAll()
  }
}

const SelfAssessment = class {
  constructor(ourFinances) {
    this.sheetName = 'Self Assessment'
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName(this.sheetName)
  }
}

function allAccounts() {
  const ourFinances = new OurFinances()
  ourFinances.showAllAccounts()
}

function analyzeActiveSheet() {
  console.log(`analyzeActiveSheet started`);
  const sheet = SpreadsheetApp.getActiveSheet();
  const sheetName = sheet.getName();
  console.log(`sheetName: ${sheetName}`);
  if (sheetName[0] === '_') {
    console.log(`${sheetName} is an account sheet`);
    const accountSheet = new AccountSheet(sheet);
    accountSheet.analyzeSheet();
  } else {
    console.log(`${sheetName} is NOT an account sheet`);
  }
  console.log(`analyzeActiveSheet finished`);
}

function applyAccountSettings() {
  const sheet = getActiveSheet();
  const sheetName = sheet.getName();
  if (sheetName[0] === "_") {
    console.log(`sheetName '${sheetName}' begins with an underscore`);
  } else {
    throw new Error(`sheetName does NOT begin with an underscore`);

  }
}

function applyDescriptionReplacements() {
  const DESCRIPTION_REPLACEMENTS_SHEET_NAME = 'Description replacements',
    START_ROW = 2,
    DESCRIPTION_COL = 2;

  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  const sheet = spreadsheet.getActiveSheet();
  const sheetName = sheet.getName();
  if (sheetName === DESCRIPTION_REPLACEMENTS_SHEET_NAME) {
    throw new Error(`Cannot applyDescriptionReplacements to '${sheetName}'`);
  }
  checkDescriptionHeader(sheet, DESCRIPTION_COL);
  console.log(`Processing sheet: ${sheetName}`);

  const lastRow = sheet.getLastRow();
  const numRows = lastRow + 1 - START_ROW;

  const range = sheet.getRange(START_ROW, DESCRIPTION_COL, numRows, 1);
  const values = range.getValues();

  let numReplacements = 0;

  const replacementsMap = getReplacementsMap(spreadsheet, DESCRIPTION_REPLACEMENTS_SHEET_NAME);

  for (let row = 0; row < values.length; row++) {
    const description = values[row][0];
    if (replacementsMap.hasOwnProperty(description)) {
      values[row][0] = replacementsMap[description];
      numReplacements++;
    }
  }

  if (numReplacements > 0) {
    range.setValues(values);
    console.log(`Updated ${numReplacements} values in sheet: ${sheetName}`);
  } else {
    console.log(`No replacements made in sheet: ${sheetName}`);
  }
}

function balanceSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const balanceSheet = new BalanceSheet(spreadsheet);

  balanceSheet.getSheet().setActiveCell(spreadsheet.getRangeByName("bottom_line"));
}

function budget() {
  goToSheet('Budget')
}

function budgetAnnualTransactions() {
  goToSheet('Budget Annual transactions')
}

function budgetMonthlyTransactions() {
  goToSheet('Budget monthly transactions')
}

function budgetOneOffTransactions() {
  goToSheet('Budget one-off transactions')
}

function budgetPredictedSpend() {
  goToSheet('Budget predicted spend')
}

function budgetWeeklyTransactions() {
  goToSheet('Budget weekly transactions')
}

function checkDependencies() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const dependencies = new Dependencies(spreadsheet)
  dependencies.updateAllDependencies()
}

function checkDescriptionHeader(sheet, col) {
  const headerValue = sheet.getRange(1, col).getValue();
  console.log(`Header value: ${headerValue}`);
  if (!headerValue.startsWith("Description")) {
    throw new Error(`Unexpected description header '${headerValue}' in sheet: ${sheet.getName()}`);
  }
}

function checkFixedAmounts(e) {
  const ourFinances = new OurFinances()
  ourFinances.checkFixedAmounts()
}

function cloneDate(date) {
  return new Date(date.getTime())
}

function convertCurrentColumnToUppercase() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const activeRange = sheet.getActiveRange();
  const START_ROW = 2;
  const column = activeRange.getColumn();

  const lastRow = sheet.getLastRow();
  const numRows = lastRow + 1 - START_ROW;

  const range = sheet.getRange(START_ROW, column, numRows, 1);
  const values = range.getValues();
  const uppercasedValues = values.map(row => [row[0].toString().toUpperCase()]);

  range.setValues(uppercasedValues);
}

function createAccountsMenu() {
  const accountSheetNames = listSheetNames('account');

  // Check if any accounts are found
  if (accountSheetNames.length === 0) {
    SpreadsheetApp.getUi().alert('No account sheets found!');
    return;
  }

  const itemArray = [];

  for (const accountSheetName of accountSheetNames) {
    const funName = "dynamicAccount" + accountSheetName;
    itemArray.push([accountSheetName, funName]);
  }

  createUiMenu('Accounts', itemArray);
}

function createGasMenu() {
  console.log('createGasMenu started')
  const itemArray = [
    ['All accounts', 'allAccounts'],
    ['Analyze active sheet', 'analyzeActiveSheet'],
    ['Apply Description replacements', 'applyDescriptionReplacements'],
    ['Balance sheet', 'balanceSheet'],
    ['Check dependencies', 'checkDependencies'],
    ['Convert current column to uppercase', 'convertCurrentColumnToUppercase'],
    ['Daily update', 'dailyUpdate'],
    ['Monthly update', 'monthlyUpdate'],
    ['Open accounts', 'openAccounts'],
    ['Sort sheet order', 'sortGoogleSheets'],
    ['Trim all sheets', 'trimGoogleSheets'],
    ['Trim sheet', 'trimGoogleSheet'],
  ]
  createUiMenu('GAS Menu', itemArray)
  console.log('createGasMenu finished')
}

function createSectionsMenu() {
  console.log('createSectionsMenu started')

  const ui = SpreadsheetApp.getUi();
  const menu = ui.createMenu('Sections')
    .addSubMenu(ui.createMenu('Budget')
      .addItem('Budget', 'budget')
      .addItem('Budget annual transactions', 'budgetAnnualTransactions')
      .addItem('Budget monthly transactions', 'budgetMonthlyTransactions')
      .addItem('Budget one-off transactions', 'budgetOneOffTransactions')
      .addItem('Budget predicted spend', 'budgetPredictedSpend')
      .addItem('Budget weekly transactions', 'budgetWeeklyTransactions')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('Categories')
      .addItem('4 All transactions by date', 'goToSheetTransactionsByDate')
      .addItem('5 Assign categories', 'goToSheetTransactionsCategories')
      .addItem('1 Categories', 'goToSheetCategories')
      .addItem('Category clash', 'goToSheetCategoryClash')
      .addItem('7 Merge transactions', 'mergeTransactions')
      .addItem('2 Not in transaction categories', 'goToSheetNotInTransactionCategories')
      .addItem('6 Transactions builder', 'goToSheetTransactionsBuilder')
      .addItem('3 Uncategorised by date', 'goToSheetUnlabelledByDate')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('Charlie')
      .addItem('Charlie\'s transactions', 'goToSheet_CVITRA')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('Fownes Street')
      .addItem('Fownes Street Halifax account', 'goToSheet_AHALIF')
      .addItem('Fownes Street Ian B HMRC records', 'goToSheet_SVI2TJ')
      .addItem('Fownes Street IRF transactions', 'goToSheet_SVIIRF')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('Glenburnie')
      .addItem('Glenburnie investment loan', 'goToSheet_SVIGBL')
      .addItem('Glenburnie loan', 'goToSheetLoanGlenburnie')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('Self Assessment (SA)')
      .addItem('Childcare', 'goToSheetHMRCTransactionsSummary')
      .addItem('Fownes Street', 'goToSheetHMRCTransactionsSummary')
      .addItem('HMRC Transactions Summary', 'goToSheetHMRCTransactionsSummary')
      .addItem('Property Management', 'goToSheetHMRCTransactionsSummary')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('SW18 3PT')
      .addItem('Home Assistant inventory', 'goToSheetSW183PTInventory')
      .addItem('Inventory', 'goToSheetSW183PTInventory')
    )
    .addSeparator()
    .addItem('Xfers mismatch', 'goToSheetXfersMismatch')
    .addToUi();

  console.log('createSectionsMenu finished')
}

function createUiMenu(menuCaption, menuItemArray) {
  const ui = SpreadsheetApp.getUi();
  const menu = ui.createMenu(menuCaption);

  menuItemArray.forEach(([itemName, itemFunction]) => {
    menu.addItem(itemName, itemFunction);
  });

  menu.addToUi();
}

function dailySorts() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheetsToSort = [
    "Bank accounts",
    "Budget monthly transactions",
    "Budget weekly transactions",
    "Description replacements",
    "Transactions categories",
  ];
  sheetsToSort.forEach(sheetName => {
    const sheet = spreadsheet.getSheetByName(sheetName);
    if (sheet) {
      sortSheetByFirstColumnOmittingHeader(sheet);
    } else {
      throw new Error(`${sheetName} not found`);
    }
  });
}

function dailyUpdate() {
  const ourFinances = new OurFinances();
  ourFinances.bankAccounts.showDaily();
}

function emailUpcomingPayments() {
  const ourFinances = new OurFinances()
  ourFinances.emailUpcomingPayments()
}

const findAllNamedRangeUsage = () => {
  const sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  const namedRanges = SpreadsheetApp.getActiveSpreadsheet().getNamedRanges();
  const rangeUsage = [];

  if (!namedRanges.length) {
    console.log('No named ranges found in this spreadsheet.');
    return;
  }

  // Extract the named range names
  const namedRangeNames = namedRanges.map(range => range.getName());

  sheets.forEach(sheet => {
    const formulas = sheet.getDataRange().getFormulas();

    formulas.forEach((rowFormulas, rowIndex) => {
      rowFormulas.forEach((formula, colIndex) => {
        // Only track cells containing named ranges
        if (formula) {
          namedRangeNames.forEach(name => {
            if (formula.includes(name)) {
              const cellRef = sheet.getRange(rowIndex + 1, colIndex + 1).getA1Notation();
              rangeUsage.push(`Sheet: ${sheet.getName()} - Cell: ${cellRef} - Name: ${name}`);
            }
          });
        }
      });
    });
  });

  if (rangeUsage.length > 0) {
    console.log('Named range(s) found in the following cells:');
    console.log(rangeUsage.join('\n'));
  } else {
    console.log('No named ranges found in any formulas.');
  }
};

const findNamedRangeUsage = () => {
  findUsageByNamedRange("BRIAN_HALIFAX_BALANCE")
}

const findUsageByNamedRange = (namedRange) => {
  const sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  const rangeUsage = [];

  sheets.forEach(sheet => {
    const formulas = sheet.getDataRange().getFormulas();

    formulas.forEach((rowFormulas, rowIndex) => {
      rowFormulas.forEach((formula, colIndex) => {
        if (formula.includes(namedRange)) {
          const cellRef = sheet.getRange(rowIndex + 1, colIndex + 1).getA1Notation();
          rangeUsage.push(`Sheet: ${sheet.getName()} - Cell: ${cellRef}`);
        }
      });
    });
  });

  if (rangeUsage.length > 0) {
    console.log(`Named range '${namedRange}' found in the following cells:`);
    console.log(rangeUsage.join("\n"));
  } else {
    console.log(`Named range '${namedRange}' not found in any formulas.`);
  }
}

function getAmountAsGBP(amount) {
  const gbPound = new Intl.NumberFormat(getLocale(), {
    style: 'currency',
    currency: 'GBP',
  });

  return gbPound.format(amount)
}

function getDayName(date) {
  const dayName = date.toLocaleDateString(getLocale(), { weekday: 'long' })
  return dayName
}

// The getDate() method of Date instances returns the day of the month for this date according to local time.
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getDate
function getDayOfMonth(date) {
  return date.getDate()
}

function getDtf() {
  return new Intl.DateTimeFormat(getLocale())
}

function getFirstRowRange(sheet) {
  const lastColumn = sheet.getLastColumn(); //console.log(lastColumn);
  const firstRowRange = sheet.getRange(1, 1, 1, lastColumn); console.log(firstRowRange);
  return firstRowRange;
}

// https://developers.google.com/apps-script/reference/utilities/utilities#formatDate(Date,String,String)
function getFormattedDate(date, timeZone, format) {
  return Utilities.formatDate(date, timeZone, format)
}

function getLastUpdatedColumn(sheet) {
  const lastUpdated = "Last Updated"
  let lastUpdatedColumn
  const firstRowRange = getFirstRowRange(sheet)
  const values = firstRowRange.getValues()
  for (let row in values) {
    for (let col in values[row]) {
      const cell = values[row][col]

      newCell = cell.replace(/\n/g, " ")

      if (newCell == lastUpdated) {
        const lastUpdatedColumnNbr = 1 + parseInt(col, 10)
        const lastUpdatedCell = firstRowRange.getCell(1, lastUpdatedColumnNbr)
        const lastUpdatedColumnA1 = lastUpdatedCell.getA1Notation()
        lastUpdatedColumn = lastUpdatedColumnA1.replace(/[0-9]/g, '')
        break;
      }
    }
  }

  return lastUpdatedColumn;
}

function getLocale() {
  return 'en-GB'
}

function getMonthIndex(date) {
  return date.getMonth();
}

function getMonthName(date) {
  return date.toLocaleDateString(this.locale, { month: 'long' });
}

const getMyEmailAddress = () => {
  // Use optional chaining to safely access the email address
  const myEmailAddress = getPrivateData()?.['MY_EMAIL_ADDRESS'];

  // Check if the email address exists and log accordingly
  if (myEmailAddress) {
    console.log(`myEmailAddress: ${myEmailAddress}`);
    return myEmailAddress;
  } else {
    console.error('MY_EMAIL_ADDRESS not found in private data');
    return null; // Return null if the email is not found
  }
}

// The getDate() method of Date instances returns the day of the month for this date according to local time.
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getDate
function getNewDate(date) {
  let newDate;
  if (date) {
    newDate = new Date(date);
  } else {
    newDate = new Date();
  }
  return newDate;
}

function getOrdinal(number) {
  let selector;

  if (number <= 0) {
    selector = 4;
  } else if ((number > 3 && number < 21) || number % 10 > 3) {
    selector = 0;
  } else {
    selector = number % 10;
  }

  return number + ['th', 'st', 'nd', 'rd', ''][selector];
}

function getOrdinalDate(date) {
  const dayOfMonth = this.getDayOfMonth(date);
  const ordinal = this.getOrdinal(dayOfMonth);
  const monthName = this.getMonthName(date);
  const fullYear = date.getFullYear();

  return `${ordinal} of ${monthName} ${fullYear}`;
}

const getPrivateData = () => {
  console.log('listPrivateData started');

  const privateDataId = '1hxcINN1seSzn-sLPI25KmV9t4kxLvZlievc0X3EgMhs';
  const sheet = SpreadsheetApp.openById(privateDataId);

  if (!sheet) {
    console.log("Sheet 'Private Data' not found");
    return;
  }

  // Get data from sheet without header row
  const values = sheet.getDataRange().getValues().slice(1);

  if (values.length === 0) {
    console.log('Sheet is empty');
    return;
  }

  let keyValuePairs = {};

  values.forEach(([key, value]) => {
    if (key && value) {
      console.log(`key: ${key}, value: ${value}`);
      if (key && value) {
        keyValuePairs[key] = value; // Store the key-value pair in the object
      }
    } else {
      console.log(`Invalid key-value pair: key=${key}, value=${value}`);
    }
  });
  console.log(keyValuePairs);

  console.log('listPrivateData finished');

  return keyValuePairs;
}

function getReplacementHeadersMap() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const bankAccounts = spreadsheet.getSheetByName('Bank accounts');
  if (!bankAccounts) {
    throw new Error(`Sheet named 'Bank accounts' not found.`);
  }

  const data = bankAccounts.getDataRange().getValues().slice(1);

  return data
    .reduce((map, [date, description, credit, debit, note]) => {
      map[description] = replacement;
      return map;
    }, {});
}

function getReplacementsMap(spreadsheet, sheetName) {
  const replacementsSheet = spreadsheet.getSheetByName(sheetName);
  if (!replacementsSheet) {
    throw new Error(`Sheet named '${sheetName}' not found.`);
  }

  const replacements = replacementsSheet.getDataRange().getValues().slice(1);

  return replacements
    .reduce((map, [description, replacement]) => {
      map[description] = replacement;
      return map;
    }, {});
}

function getSeasonName(date) {
  const seasons = ['Winter', 'Spring', 'Summer', 'Autumn'];

  const monthSeasons = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0];

  const monthIndex = getMonthIndex(date);
  const seasonIndex = monthSeasons[monthIndex];

  return seasons[seasonIndex];
}

function getSpreadsheetNameById(id) {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const dependencies = new Dependencies(spreadsheet);

  return dependencies.getSpreadsheetNameById(id);
}

function getToday(options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) {
  const date = new Date();
  const locale = getLocale();
  let today;

  try {
    const dtf = new Intl.DateTimeFormat(locale, options);
    today = dtf.format(date);
  } catch (error) {
    console.log(`Error formatting date: ${error.message}`);
    today = date.toLocaleDateString(locale, options); // Fallback to toLocaleDateString
  }

  return today;
}

function goToSheet(sheetName) {
  // Get the spreadsheet object.
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  // Get the sheet by name.
  const sheet = spreadsheet.getSheetByName(sheetName);

  // Check if the sheet exists before trying to activate it.
  if (sheet) {
    sheet.activate();
  } else {
    console.log('Sheet not found: ' + sheetName);
  }
}

function goToSheetLastRow(sheetName) {
  // Get the spreadsheet object.
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  // Get the sheet by name and activate it.
  const sheet = spreadsheet.getSheetByName(sheetName);

  // Get the last row with content
  const lastRow = sheet.getLastRow();

  // Get the first cell in the last row (Column A)
  const cell = sheet.getRange(lastRow, 1);

  // Activate the cell
  sheet.setActiveRange(cell);

  const accountSheet = new AccountSheet(sheet);
  accountSheet.analyzeSheet();
}

function goToSheet_AHALIF() {
  goToSheet('_AHALIF')
}

function goToSheet_CVITRA() {
  goToSheet('_CVITRA')
}

function goToSheet_SVI2TJ() {
  goToSheet('_SVI2TJ')
}

function goToSheet_SVIGBL() {
  goToSheet('_SVIGBL')
}

function goToSheet_SVIIRF() {
  goToSheet('_SVIIRF')
}

function goToSheetCategories() {
  goToSheet('Categories')
}

function goToSheetCategoryClash() {
  goToSheet('Category clash')
}

function goToSheetHMRCTransactionsSummary() {
  goToSheet('HMRC Transactions Summary')
}

function goToSheetLoanGlenburnie() {
  goToSheet('Loan Glenburnie')
}

function goToSheetNotInTransactionCategories() {
  goToSheet('Not in transaction categories')
}

function goToSheetSW183PTInventory() {
  goToSheet('SW18 3PT inventory')
}

function goToSheetTransactionsBuilder() {
  goToSheet('Transactions builder')
}

function goToSheetTransactionsByDate() {
  goToSheet('Transactions by date')
}

function goToSheetTransactionsCategories() {
  goToSheet('Transactions categories')
}

function goToSheetUnlabelledByDate() {
  goToSheet('Uncategorised by date')
}

function goToSheetXfersMismatch() {
  goToSheet('Xfers mismatch')
}

function isCellAccountBalance(sheet, column) {
  const accountBalance = "Account Balance";

  let isCellAccountBalance = false;

  const firstRowRange = getFirstRowRange(sheet);

  const values = firstRowRange.getValues()
  for (const row in values) {
    const cell = values[row][column - 1];
    console.log(cell);

    newCell = cell.replace(/\n/g, " ");
    console.log(newCell);

    if (newCell == accountBalance) {
      isCellAccountBalance = true;
      break;
    }
  }

  return isCellAccountBalance;
}

function isCellADate(cell) {
  // Get the value of the specified cell
  const cellValue = cell.getValue();

  // Check if the value is a Date object
  if (Object.prototype.toString.call(cellValue) === '[object Date]' && !isNaN(cellValue.getTime())) {
    console.log("Cell contains a valid date.");
    return true;
  } else {
    console.log("Cell does NOT contain a date.");
    return false;
  }
}

/**
 * Checks if the given range represents a single cell.
 * 
 * @param {Range} range - The range to check.
 * @returns {boolean} - Returns true if the range contains only one cell, otherwise false.
 */
function isSingleCell(range) {
  if (!range || typeof range.getNumColumns !== 'function' || typeof range.getNumRows !== 'function') {
    throw new Error('Invalid input: Expected a Range object.');
  }

  return range.getNumColumns() === 1 && range.getNumRows() === 1;
}

function listSheetNames(sheetNameType) {
  console.log('listSheetNames started');
  console.log(`sheetNameType: ${sheetNameType}`);

  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const spreadsheetName = spreadsheet.getName();
  console.log(`spreadsheetName: ${spreadsheetName}`);

  const sheets = spreadsheet.getSheets();
  console.log(`${spreadsheetName} has ${sheets.length} sheets.`);

  // Constants for budget-related sheet names
  const budgetSheetNames = [
    'Budget annual transactions',
    'Budget monthly transactions',
    'Budget one-off transactions',
    'Budget predicted spend',
    'Budget weekly transactions'
  ];

  // Process based on sheetNameType
  switch (sheetNameType) {
    case 'account':
      // Filter sheets where the name starts with '_'
      return sheets.map(sheet => sheet.getName())
        .filter(sheetName => sheetName.startsWith('_'));

    case 'all':
      // Return all sheet names
      return sheets.map(sheet => sheet.getName());

    case 'budget':
      // Return the predefined budget sheet names
      return budgetSheetNames;

    default:
      throw new Error(`Unexpected sheetNameType: ${sheetNameType}`);
  }
  console.log('listSheetNames finished')
}

function mergeTransactions() {
  const { getSheetByName } = SpreadsheetApp.getActiveSpreadsheet();

  // Destructuring to cleanly get sheets
  const transactionsBuilderSheet = getSheetByName("Transactions Builder");

  if (!transactionsBuilderSheet) {
    console.log("Sheet 'Transactions Builder' not found");
    return;
  }

  const transactionsSheet = getSheetByName("Transactions");

  if (!transactionsSheet) {
    console.log("Sheet 'Transactions' not found");
    return;
  }

  // Batch getting the formula values from the "Transactions Builder" sheet
  const formulas = transactionsBuilderSheet.getRange("G3:G4").getValues();

  // Logging both formulas
  console.log(`keyFormula: =${formulas[0][0]}`);
  console.log(`secondFormula: =${formulas[1][0]}`);

  // Set the formulas in a single batch operation
  transactionsSheet.getRange("A1:B1").setFormulas([
    [`=${formulas[0][0]}`, `=${formulas[1][0]}`]
  ]);

  transactionsSheet.activate();
}

function monthlyUpdate() {
  const ourFinances = new OurFinances();
  ourFinances.bankAccounts.showMonthly();
}

function onChange(e) {
  setLastUpdatedOnAccountBalanceChange(e);
}

// onDateChange is not a Google trigger; it must be created under Triggers (time based)!!!
function onDateChange() {
  emailUpcomingPayments();
  dailySorts();
}

function onEdit(e) {
  setLastUpdatedOnAccountBalanceChange(e);
  checkFixedAmounts(e)
}

function onOpen() {
  console.log('onOpen started');

  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  // Displaying a temporary notification to the user
  spreadsheet.toast("Please wait while I do a few tasks", "Please wait!", 500);

  // Calling custom menu creation functions
  createAccountsMenu();
  createGasMenu();
  createSectionsMenu();

  // Notifying the user that the tasks are finished
  spreadsheet.toast("You can do your thing now.", "I'm finished!", 3);

  console.log('onOpen finished');
}

function openAccounts() {
  const ourFinances = new OurFinances();
  ourFinances.bankAccounts.showOpenAccounts();
}

function sendEmail(recipient, subject, body, options) {
  return GmailApp.sendEmail(recipient, subject, body, options);
}

function sendMeEmail(subject, emailBody, options) {
  const body = `${subject}\n\n${emailBody}`;
  return sendEmail(getMyEmailAddress(), subject, body, options);
}

function setLastUpdated(cell) {
  const lastUpdated = new Date();
  cell.setValue(lastUpdated);
}

function setLastUpdatedOnAccountBalanceChange(e) {
  const range = e.range;

  // Check if the range is a single cell
  if (!isSingleCell(range)) return;

  const column = range.getColumn();
  const sheet = range.getSheet();

  // Check if the cell corresponds to an account balance
  if (!isCellAccountBalance(sheet, column)) return;

  // Get the row of the changed cell
  const row = range.getRow();

  // Determine the "Last Updated" column and update the timestamp
  const lastUpdatedColumn = getLastUpdatedColumn(sheet);
  if (lastUpdatedColumn) {
    const lastUpdateCell = sheet.getRange(row, lastUpdatedColumn);
    setLastUpdated(lastUpdateCell);
  }
}

function setupDaysIterator(startDate, logIt = () => { }) {
  const getNextResult = (iteratorDate) => {
    const date = cloneDate(iteratorDate);  // Default date in long format
    const day = getDtf().format(date);     // 19/01/1964
    const dayName = getDayName(date);      // Sunday
    const dayOfMonth = getDayOfMonth(date);  // 29
    const season = getSeasonName(date, logIt);  // Winter, Spring, Summer, Autumn

    // Return result as an object
    return { date, day, dayName, dayOfMonth, season };
  };

  const iteratorDate = new Date(startDate);
  const first = getNextResult(iteratorDate);

  const iterator = {
    next: () => {
      iteratorDate.setDate(iteratorDate.getDate() + 1);
      return getNextResult(iteratorDate);
    }
  };

  return { first, iterator };
}

function showRowCountForAllSheets() {
  // Get the active spreadsheet
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  // Get all the sheets in the spreadsheet
  const sheets = spreadsheet.getSheets();

  // Loop through each sheet
  for (let i = 0; i < sheets.length; i++) {
    const sheet = sheets[i];

    // Get the sheet name
    const sheetName = sheet.getName();

    // Get the last row with content (row count)
    const lastRow = sheet.getLastRow();

    // Log the row count or display it in a message box
    console.log("Sheet: " + sheetName + " has " + lastRow + " rows.");

    // Optionally, display in a message box
    // Browser.msgBox("Sheet: " + sheetName + " has " + lastRow + " rows.");
  }
}

function showTransactionsBuilderSteps() {
  // Get the active spreadsheet
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  // Get all the sheets in the spreadsheet
  const sheets = spreadsheet.getSheets();

  // Loop through each sheet
  for (let i = 0; i < sheets.length; i++) {
    const sheet = sheets[i];

    // Get the sheet name
    const sheetName = sheet.getName();

    // Only consider 'accounts' sheets
    if (sheetName[0] === '_') {
      // Get the last row with content (row count)
      const lastRow = sheet.getLastRow();

      // Log the row count or display it in a message box
      console.log("Sheet: " + sheetName + " has " + lastRow + " rows.");

      if (lastRow > 2) {
        const cell = sheet.getRange("A2");
        if (!isCellADate(cell)) {
          crash(sheetName + "!A2 is NOT a date.")
        }
      }

    }
  }
}

function sortGoogleSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Store all the worksheets in this array
  const sheetNameArray = [];
  const sheets = ss.getSheets();
  sheets.forEach(sheet => {
    sheetNameArray.push(sheet.getName())
  })

  sheetNameArray.sort();

  // Reorder the sheets.
  for (let j = 0; j < sheets.length; j++) {
    ss.setActiveSheet(ss.getSheetByName(sheetNameArray[j]));
    ss.moveActiveSheet(j + 1);
  }
}

function sortSheetByFirstColumn(sheet) {
  // Get the range that contains data
  const dataRange = sheet.getDataRange();

  // Sort the range by the first column (column 1) in ascending order
  dataRange.sort({ column: 1, ascending: true });
}

function sortSheetByFirstColumnOmittingHeader(sheet) {
  // Get the range that contains data
  const dataRange = sheet.getDataRange();

  // Get the number of rows and columns
  const numRows = dataRange.getNumRows();
  const numCols = dataRange.getNumColumns();

  // Get the range excluding the first row
  const rangeToSort = sheet.getRange(2, 1, numRows - 1, numCols);

  // Sort the range by the first column (column 1) in ascending order
  rangeToSort.sort({ column: 1, ascending: true });
}

function trimGoogleSheet() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheetName = spreadsheet.activeSheetName
  const sheet = spreadsheet.getSheetByName(sheetName)

  sheet.trimSheet()
}

function trimGoogleSheets() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  const sheets = spreadsheet.getSheets();
  sheets.forEach(sheet => {
    sheet.trimSheet();
  });
}

console.log('Setting up dynamic accounts functions')
const accountSheetNames = listSheetNames('account');
console.log(`There are ${accountSheetNames.length} account sheets.`);
accountSheetNames.forEach(sheetName => {
  const funName = `dynamicAccount${sheetName}`;
  this[funName] = () => goToSheetLastRow(sheetName);
});
console.log('Setting up dynamic accounts functions complete')