const AccountBalances = class {
  static get COL_ACCOUNT_KEY() { return 1; }
  static get COL_BALANCE() { return 4; }
  static get SHEET_NAME() { return 'Account balances'; }
  constructor() {
    this.sheet = new IswSheet(BalanceSheet.SHEET_NAME);

    this.log(`Initialized sheet: ${this.getSheetName()}`);
  }
}

const AccountSheet = class {
  static get COL_BALANCE() { return 8; }
  static get COL_COUNTERPARTY() { return 6; }
  static get COL_COUNTERPARTY_DATE() { return 7; }
  static get COL_CREDIT() { return 3; }
  static get COL_DATE() { return 1; }
  static get COL_DEBIT() { return 4; }
  static get COL_DESCRIPTION() { return 2; }
  static get COL_NOTE() { return 5; }

  static get ROW_DATA_STARTS() { return 2; }

  static get HEADERS() {
    return ['Date', 'Description', 'Credit', 'Debit', 'Note', 'CPTY', 'CPTY Date', 'Balance'];
  }

  static get MINIMUM_COLUMNS() { return 8; }

  constructor(iswSheet) {
    Logger.log('AccountSheet.constructor started');
    Logger.log(`getType(iswSheet): ${getType(iswSheet)}`);
    if (iswSheet) {
      const sheetName = iswSheet.getSheetName();
      if (sheetName[0] === '_') {
        Logger.log(`${sheetName} is an account sheet`);
        this.sheet = iswSheet;
      } else {
        throw new Error(`${sheetName} is NOT an account sheet`);
      }
    }
    Logger.log('AccountSheet.constructor finished');
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

  applyDescriptionReplacements() {
    const descriptionReplacements = new DescriptionReplacements();
    descriptionReplacements.applyReplacements(this.sheet);
  }

  convertColumnToUppercase(column) {
    const START_ROW = 2;
    const lastRow = this.sheet.getLastRow();
    const numRows = lastRow - START_ROW + 1;

    const range = this.sheet.getRange(START_ROW, column, numRows, 1);
    const values = range.getValues().map(row => [row[0]?.toString().toUpperCase()]);

    range.setValues(values);
    this.log(`Converted column ${column} to uppercase`);
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

  get spreadsheet() {
    return this.sheet.spreadsheet;
  }

  get spreadsheetName() {
    return this.sheet.spreadsheetName;
  }

  getExpectedHeader(column) {
    return column === AccountSheet.COL_DESCRIPTION
      ? this.xLookup(this.getSheetName().slice(1), this.sheet.getParent().getSheetByName('Bank accounts'), 'A', 'AQ')
      : AccountSheet.HEADERS[column - 1];
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  log(message, level = 'info') {
    this.sheet.log(message, level);
  }

  logSheetDetails() {
    this.sheet.logSheetDetails();
  }

  setBackground(a1range, background = '#FFFFFF') {
    this.sheet.getRange(a1range).setBackground(background);
    this.log(`Background color set to ${background} for range ${a1range}`);
  }

  setColumnWidth(column, widthInPixels) {
    this.sheet.setColumnWidth(column, widthInPixels);
    this.log(`Set column ${column} width to ${widthInPixels} pixels`);
  }

  setConditionalCcyFormattingByValue(a1range) {
    const range = this.sheet.getRange(a1range);
    const rule = this.spreadsheet.newConditionalFormatRule()
      .whenNumberLessThan(0)
      .setFontColor("#FF0000")
      .setRanges([range])
      .build();

    const rules = this.sheet.getConditionalFormatRules();

    rules.push(rule);
    this.sheet.setConditionalFormatRules(rules);
  }

  setCounterpartyValidation(a1range) {
    const range = this.sheet.getRange(a1range);
    const rule = gasSpreadsheetApp.newDataValidation()
      .requireValueInRange(this.sheet.getParent().getRange('\'Bank accounts\'!$A$2:$A'), true)
      .setAllowInvalid(false)
      .setHelpText('Please select a valid counterparty.')
      .build();

    range.setDataValidation(rule);
    this.log(`Applied counterparty validation to ${a1range}`);
  }

  setDateValidation(a1range) {
    const range = this.sheet.getRange(a1range);
    const rule = gasSpreadsheetApp.newDataValidation()
      .requireDate()
      .setAllowInvalid(false)
      .setHelpText('Please enter a valid date in DD/MM/YYYY format.')
      .build();

    range.setDataValidation(rule);
    this.log(`Applied date validation to ${a1range}`);
  }

  setNumberFormat(a1range, format) {
    this.sheet.getRange(a1range).setNumberFormat(format);
    this.log(`Set number format for ${a1range} to '${format}'`);
  }

  setSheetFont(fontFamily = 'Arial', fontSize = 10, fontColor = '#000000') {
    const range = this.sheet.getDataRange();
    range.setFontFamily(fontFamily).setFontSize(fontSize).setFontColor(fontColor);
    this.log(`Set sheet font to ${fontFamily}, size ${fontSize}, color ${fontColor}`);
  }

  setSheetFormatting() {
    this.sheet.setConditionalFormatRules([]);
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
    const frozenRows = this.sheet.getFrozenRows();
    if (frozenRows !== 1) {
      throw new Error(`There should be 1 frozen row; found ${frozenRows}`);
    }
    this.log('Frozen rows validation passed');
  }

  validateHeaders() {
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
      throw new Error(`Sheet ${this.getSheetName()} requires at least ${AccountSheet.MINIMUM_COLUMNS} columns, but found ${lastColumn}`);
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
  constructor() {
    this.sheet = new IswSheet(BalanceSheet.SHEET_NAME);

    this.log(`Initialized sheet: ${this.getSheetName()}`);
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  getSheet() {
    return this.sheet;
  }

  log(message, level = 'info') {
    const logPrefix = `[${this.getSheetName()}] `;
    const logMessage = `${logPrefix}${message}`;
    level === 'error' ? Logger.log(`ERROR: ${logMessage}`) : Logger.log(logMessage);
  }

  setActiveCell(a1cellRef) {
    this.sheet.setActiveCell(a1cellRef);
  }
}

const BankAccounts = class {
  static get COL_BALANCE_UPDATED() { return 19; }
  static get COL_CHECK_BALANCE_FREQUENCY() { return 12; }
  static get COL_KEY() { return 1; }
  static get COL_KEY_LABEL() { return 'A'; }
  static get COL_OWNER_CODE() { return 3; }
  static get OWNER_CODE_BRIAN() { return 'A'; }
  static get OWNER_CODE_CHARLIE() { return 'C'; }
  static get OWNER_CODE_LINDA() { return 'L'; }
  static get SHEET_NAME() { return 'Bank accounts'; }

  constructor() {
    this.sheet = new IswSheet(BankAccounts.SHEET_NAME);

    if (!this.sheet) {
      throw new Error(`Sheet '${this.getSheetName()}' not found.`);
    }

    this.log(`Initialized sheet: ${this.getSheetName()}`);
  }

  applyFilters(filters) {
    const sheet = this.sheet;

    // Clear any existing filters
    this.removeFilter();

    const filter = sheet.getDataRange().createFilter();

    filters.forEach(item => {
      const criteria = item.hideValues === null
        ? iswActiveSpreadsheet.newFilterCriteria().whenCellEmpty().build()
        : iswActiveSpreadsheet.newFilterCriteria().setHiddenValues(item.hideValues).build();

      filter.setColumnFilterCriteria(item.column, criteria);
    });

    this.log(`Filters applied: ${JSON.stringify(filters)}`);
  }

  getDataRange() {
    return this.sheet.getDataRange();
  }

  getSheetName() {
    return this.sheet.getSheetName();
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
    const logPrefix = `[${this.getSheetName()}] `;
    const logMessage = `${logPrefix}${message}`;
    level === 'error' ? Logger.log(`ERROR: ${logMessage}`) : Logger.log(logMessage);
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
    sheet.activate();

    this.log("All columns shown");
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

    const columnsToHide = ['C:L', 'N:O', 'Q:Q', 'S:AN', 'AQ:AQ'];
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

  updateLastUpdatedByKey(key) {
    const row = findRowByKey(BankAccounts.SHEET_NAME, BankAccounts.COL_KEY_LABEL, key);
    this.log(`row: ${row}`);

    const lastUpdateCell = this.sheet.getRange(row, BankAccounts.COL_BALANCE_UPDATED);
    lastUpdateCell.setValue(new Date());
  }
}

const BankDebitsDue = class {
  static get COL_ACCOUNT_KEY() { return 0; }
  static get COL_CHANGE_AMOUNT() { return 1; }

  constructor(ourFinances) {
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName('Bank debits due');
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    // Check if the sheet exists
    if (!this.sheet) {
      throw new Error(`Sheet "${this.getSheetName()}" not found in the spreadsheet.`);
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
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName('Budget annual transactions');
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    if (!this.sheet) {
      throw new Error(`Sheet "${this.getSheetName()}" not found.`);
    }
  }

  // Get all scheduled transactions from the sheet
  getScheduledTransactions() {
    return this.sheet.getDataRange().getValues();
  }

  // Main method to get upcoming debits
  getUpcomingDebits() {
    Logger.log('BudgetAnnualTransactions:getUpcomingDebits');
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
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName('Budget monthly transactions')
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    if (!this.sheet) {
      throw new Error(`Sheet "${this.getSheetName()}" not found.`);
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
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName('Budget one-off transactions');
    this.howManyDaysAhead = ourFinances.howManyDaysAhead;

    if (!this.sheet) {
      throw new Error(`Sheet "${this.getSheetName()}" not found.`);
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
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName('Budget weekly transactions')
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
        Logger.log(`daySelected: ${daySelected}`)

        const formattedDaySelected = getFormattedDate(new Date(daySelected), "GMT+1", "dd/MM/yyyy")
        Logger.log(`formattedDaySelected: ${formattedDaySelected}`)

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
  static get SHEET_NAME() { return 'Check fixed amounts'; }

  constructor() {
    this.sheet = new IswSheet(CheckFixedAmounts.SHEET_NAME);
  }

  getValues() {
    return this.sheet.getDataRange().getValues();
  }

  reportMismatchesX() {
    const values = this.getValues();

    values.forEach(row => {
      if (row[CheckFixedAmounts.COL_MISMATCH] == 'Mismatch') {
        const mismatchMessage = `${row[CheckFixedAmounts.COL_DESCRIPTION]}: Dynamic amount (${row[CheckFixedAmounts.COL_DYNAMIC_AMOUNT]}) does not match fixed amount (${row[CheckFixedAmounts.COL_FIXED_AMOUNT]})`
        alert(mismatchMessage)
      }
    })
  }
  reportMismatches() {
    const values = this.getValues();

    values.forEach(row => {
      // Guard clause: skip rows with missing or undefined data
      if (!row || row.length === 0) return;

      const mismatchColumn = CheckFixedAmounts.COL_MISMATCH;
      const descriptionColumn = CheckFixedAmounts.COL_DESCRIPTION;
      const dynamicAmountColumn = CheckFixedAmounts.COL_DYNAMIC_AMOUNT;
      const fixedAmountColumn = CheckFixedAmounts.COL_FIXED_AMOUNT;

      if (row[mismatchColumn] === 'Mismatch') {
        const mismatchMessage = `${row[descriptionColumn]}: Dynamic amount (${row[dynamicAmountColumn]}) does not match fixed amount (${row[fixedAmountColumn]})`;
        Logger.log(`Mismatch found: ${mismatchMessage}`); // Optional logging for debugging
        alert(mismatchMessage);
      }
    });
  }
}

const Dependencies = class {
  static get SHEET_NAME() { return 'Dependencies'; }
  constructor() {
    this.sheet = new IswSheet(Dependencies.SHEET_NAME);
  }

  getAllDependencies() {
    Logger.log("Dependencies.getAllDependencies");

    if (typeof this.allDependencies !== 'undefined') {
      Logger.log(`getAllDependencies: using cached dependencies: ${this.allDependencies}`);
      return this.allDependencies;
    }

    // Retrieve dependencies if not cached
    let allDependencies = this.getSheet().getDataRange().getValues();

    // Remove the first row (header or irrelevant row)
    allDependencies.shift();

    // Cache the result for future use
    this.allDependencies = allDependencies;

    Logger.log(`getAllDependencies: freshly loaded dependencies: ${allDependencies}`);

    return allDependencies;
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  getSpreadsheetNameById(spreadsheetId) {
    try {
      const spreadsheet = new IswSpreadsheet(spreadsheetId);
      return spreadsheet.spreadsheetName;
    } catch (error) {
      Logger.log(`Error fetching spreadsheet with ID: ${spreadsheetId}. ${error.message}`);
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

const DescriptionReplacements = class {
  static get SHEET_NAME() { return 'Description replacements'; }

  constructor() {
    this.sheet = new IswSheet(DescriptionReplacements.SHEET_NAME);

    this.log(`Initialized sheet: ${this.getSheetName()}`);
  }

  applyReplacements(accountSheet) {
    const accountSheetName = accountSheet.sheetName;
    if (accountSheetName === this.getSheetName()) {
      throw new Error(`Cannot applyDescriptionReplacements to '${accountSheetName}'`);
    }

    const headerValue = accountSheet.getRange(1, AccountSheet.COL_DESCRIPTION).getValue();
    Logger.log(`Header value: ${headerValue}`);
    if (!headerValue.startsWith("Description")) {
      throw new Error(`Unexpected description header '${headerValue}' in sheet: ${accountSheetName}`);
    }

    Logger.log(`Processing sheet: ${accountSheetName}`);

    const lastRow = accountSheet.getLastRow();
    const numRows = lastRow + 1 - AccountSheet.ROW_DATA_STARTS;

    const range = accountSheet.getRange(AccountSheet.ROW_DATA_STARTS, AccountSheet.COL_DESCRIPTION, numRows, 1);
    const values = range.getValues();

    let numReplacements = 0;

    const replacementsMap = this.getReplacementsMap();

    for (let row = 0; row < values.length; row++) {
      const description = values[row][0];
      if (replacementsMap.hasOwnProperty(description)) {
        values[row][0] = replacementsMap[description];
        numReplacements++;
      }
    }

    if (numReplacements > 0) {
      range.setValues(values);
      Logger.log(`Updated ${numReplacements} values in sheet: ${accountSheetName}`);
    } else {
      Logger.log(`No replacements made in sheet: ${accountSheetName}`);
    }
  }

  getReplacementsMap() {
    const replacements = this.sheet.getDataRange().getValues().slice(1);

    return replacements
      .reduce((map, [description, replacement]) => {
        map[description] = replacement;
        return map;
      }, {});
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  getSheet() {
    return this.sheet;
  }

  log(message, level = 'info') {
    const logPrefix = `[${this.getSheetName()}] `;
    const logMessage = `${logPrefix}${message}`;
    level === 'error' ? Logger.log(`ERROR: ${logMessage}`) : Logger.log(logMessage);
  }
}

const IswSheet = class {
  constructor(x = null) {
    logWithTimeInterval(getLineNumber())
    const xType = getType(x);

    if (xType === 'string') {
      const sheetName = x;
      logWithTimeInterval(getLineNumber())
      this.sheet = iswActiveSpreadsheet.getSheetByName(sheetName).sheet;
      if (!this.sheet) {
        throw new Error(`Sheet with name "${sheetName}" not found`);
      }
      this.log(`${this.getSheetName()} initialised`);
      return;
    }

    if (xType === 'Object') {
      const gasSheet = x;
      this.sheet = gasSheet;
      this.log(`952: ${this.getSheetName()} initialised`);
      return;
    }

    if (x === null) {
      Logger.log('No input provided, initializing without a sheet');
      const activeSheet = iswActiveSpreadsheet.getActiveSheet();
      if (activeSheet) {
        this.sheet = activeSheet;
        this.log(`${this.getSheetName()} initialised`);
      } else {
        this.sheet = null;
        this.log('No active sheet found. Initialised to null');
      }
      return;
    }

    // Handle unexpected types
    throw new TypeError(`Unexpected input type: ${xType}`);
  }

  get spreadsheet() {
    if (!this._spreadsheet) {
      this._spreadsheet = new IswSpreadsheet(this.sheet.getParent().getId());
    }
    return this._spreadsheet;
  }

  get spreadsheetName() {
    if (!this._spreadsheetName) {
      this._spreadsheetName = this.spreadsheet.spreadsheetName;
      this.log(`Spreadsheet: ${this._spreadsheetName}`);
    }
    return this._spreadsheetName;
  }

  activate() {
    this.sheet.activate();
  }

  clear() {
    this.sheet.clear();
  }

  deleteExcessColumns() {
    const frozenColumns = this.sheet.getFrozenColumns();
    const lastColumn = this.sheet.getLastColumn();
    const maxColumns = this.sheet.getMaxColumns();

    // Determine the start column for deletion
    const startColumn = Math.max(lastColumn + 1, frozenColumns + 2);

    const howManyColumnsToDelete = 1 + maxColumns - startColumn;

    if (howManyColumnsToDelete > 0) {
      this.sheet.deleteColumns(startColumn, howManyColumnsToDelete);
    }
  }

  deleteExcessRows() {
    const frozenRows = this.sheet.getFrozenRows()
    const lastRow = this.sheet.getLastRow();
    let startRow = lastRow + 1
    if (lastRow <= frozenRows) {
      startRow = frozenRows + 2;
    }
    const maxRows = this.sheet.getMaxRows()
    const howManyRowsToDelete = 1 + maxRows - startRow

    if (maxRows > startRow) {
      this.sheet.deleteRows(startRow, howManyRowsToDelete);
    }
  }

  getConditionalFormatRules() {
    Logger.log('IswSheet.getConditionalFormatRules started');
    return this.sheet.getConditionalFormatRules();
  }

  getDataRange() {
    return this.sheet.getDataRange();
  }

  getFilter() {
    return this.sheet.getFilter()
  }

  getFrozenRows() {
    return this.sheet.getFrozenRows()
  }

  getLastColumn() {
    return this.sheet.getLastColumn();
  }

  getLastRow() {
    return this.sheet.getLastRow();
  }

  getMaxColumns() {
    return this.sheet.getMaxColumns();
  }

  getMaxRows() {
    return this.sheet.getMaxRows();
  }

  getParent() {
    return this.sheet.getParent();
  }

  getRange(...args) {
    return this.sheet.getRange(...args);
  }

  getRangeList(...args) {
    return this.sheet.getRangeList(...args);
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  getValue(range) {
    return this.getRange(range).getValue();
  }

  hideColumn(...args) {
    return this.sheet.hideColumn(...args)
  }

  log(message, level = 'info') {
    const logPrefix = `[${this.getSheetName()}] `;
    console[level === 'error' ? 'error' : 'log'](`${logPrefix}${message}`);
  }

  logSheetDetails() {
    const lastColumn = this.sheet.getLastColumn();
    this.log('Logging sheet details...');
    this.log(`Minimum required columns: ${AccountSheet.MINIMUM_COLUMNS}`);
    this.log(`Sheet name: ${this.getSheetName()}`);
    this.log(`Last column with data: ${lastColumn}`);
    this.log(`Maximum possible columns: ${this.sheet.getMaxColumns()}`);
  }

  setActiveCell(...args) {
    this.sheet.setActiveCell(...args)
  }

  setActiveRange(range) {
    this.sheet.setActiveRange(range);
  }

  setColumnWidth(column, width) {
    return this.sheet.setColumnWidth(column, width)
  }

  setConditionalFormatRules(rules) {
    this.sheet.setConditionalFormatRules(rules);
  }

  setSheetByName(sheetName) {
    this.spreadsheet = iswActiveSpreadsheet;
    this.sheet = iswActiveSpreadsheet.getSheetByName(BalanceSheet.SHEET_NAME);

    if (!this.sheet) {
      throw new Error(`Sheet '${this.getSheetName()}' not found.`);
    }

    this.log(`Initialized sheet: ${this.getSheetName()}`);
  }

  setValue(range, value) {
    return this.getRange(range).setValue(value);
  }

  showColumns(...args) {
    return this.sheet.showColumns(...args);
  }

  trimSheet() {
    this.deleteExcessColumns();
    this.deleteExcessRows();
    return this;
  }
}

const IswSpreadsheet = class {
  constructor(spreadsheetId) {
    logWithTimeInterval(getLineNumber())
    if (spreadsheetId) {
      Logger.log(`spreadsheetId: ${spreadsheetId}`);
      try {
        this.spreadsheet = gasSpreadsheetApp.openById(spreadsheetId);
      } catch (error) {
        Logger.log(`Error opening spreadsheet with ID: ${spreadsheetId}. ${error.message}`);
        throw error;
      }
    } else {
      try {
        logWithTimeInterval(getLineNumber())
        this.spreadsheet = gasActiveSpreadsheet;

        logWithTimeInterval(getLineNumber())
      } catch (error) {
        Logger.log(`Error opening active spreadsheet: ${error.message}`);
        throw error;
      }
    }

    Logger.log(`Initialised spreadsheet: ${this.spreadsheetName}`);
  }

  get spreadsheetName() {
    return this.spreadsheet.getName();
  }

  getActiveSheet() {
    const activeSheet = this.spreadsheet.getActiveSheet();
    const activeSheetType = getType(activeSheet);
    Logger.log(`${activeSheet} has type ${activeSheetType}`);

    const iswActiveSheet = new IswSheet(activeSheet);
    const iswActiveSheetType = getType(iswActiveSheet);
    Logger.log(`${iswActiveSheet} has type ${iswActiveSheetType}`);

    return iswActiveSheet;
  }

  getSheetByName(sheetName) {
    logWithTimeInterval(getLineNumber())
    Logger.log('IswSpreadsheet.getSheetByName');
    Logger.log(`sheetName: ${sheetName}`);

    logWithTimeInterval(getLineNumber())
    const sheet = gasActiveSpreadsheet.getSheetByName(sheetName);

    logWithTimeInterval(getLineNumber())
    const iswSheet = new IswSheet(sheet);

    logWithTimeInterval(getLineNumber())
    Logger.log(`1185: iswSheet.getSheetName(): ${iswSheet.getSheetName()}`);

    return iswSheet;
  }

  getSheets() {
    Logger.log("Fetching sheets...");

    // Use map for a cleaner approach to create new IswSheet instances
    const sheets = this.spreadsheet.getSheets().map(sheet => new IswSheet(sheet));

    Logger.log(`Retrieved ${sheets.length} sheets from ${this.spreadsheetName}.`);

    return sheets;
  }

  getUrl() {
    return this.spreadsheet.getUrl();
  }

  newConditionalFormatRule() {
    return gasSpreadsheetApp.newConditionalFormatRule();
  }

  newFilterCriteria() {
    return gasSpreadsheetApp.newFilterCriteria();
  }

  toast(msg, title, timeoutSeconds) {
    this.spreadsheet.toast(msg, title, timeoutSeconds);
  }
}

const OurFinances = class {
  constructor() {
    this.spreadsheet = iswActiveSpreadsheet;
  }

  checkFixedAmounts() {
    const checkFixedAmounts = new CheckFixedAmounts()
    checkFixedAmounts.reportMismatches()
  }

  emailUpcomingPayments() {
    const subject = `Our Finances: Upcoming debits ${getToday()}`;
    Logger.log(`Subject: ${subject}`);

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

    Logger.log(`Email Body: ${emailBody}`);

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
    if (typeof this._howManyDaysAhead === 'undefined') {
      const sheetName = 'Bank debits due';
      const sheet = this.getSheetByName(sheetName);
      const searchValue = 'Look ahead';
      this._howManyDaysAhead = xLookup(searchValue, sheet, 'D', 'E');
    }
    return this._howManyDaysAhead;
  }

  get budgetMonthlyTransactions() {
    if (typeof this._budgetMonthlyTransactions === 'undefined') {
      this._budgetMonthlyTransactions = new BudgetMonthlyTransactions(this);
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

  getSheetByName(sheetName, logIt) {
    return this.spreadsheet.getSheetByName(sheetName, logIt)
  }

  showAllAccounts() {
    this.bankAccounts.showAll()
  }
}

const SelfAssessment = class {
  constructor(ourFinances) {
    this.spreadsheet = ourFinances.spreadsheet
    this.sheet = this.spreadsheet.getSheetByName('Self Assessment')
  }
}

function allAccounts() {
  const ourFinances = new OurFinances()
  ourFinances.showAllAccounts()
}

function analyzeActiveSheet() {
  Logger.log(`analyzeActiveSheet started`);
  const activeSheet = iswActiveSpreadsheet.getActiveSheet();
  Logger.log(`Processing ${activeSheet.sheetName}`);
  try {
    const accountSheet = new AccountSheet(activeSheet);
    accountSheet.analyzeSheet();
  } catch (error) {
    Logger.log(`${activeSheet.sheetName}: ${error.message}`);
  }
  Logger.log(`analyzeActiveSheet finished`);
}

const SpreadsheetSummary = class {
  static get COL_SHEET_NAME() { return 0; }
  static get COL_LAST_ROW() { return 1; }
  static get COL_LAST_COL() { return 2; }
  static get COL_MAX_ROWS() { return 3; }
  static get COL_MAX_COLS() { return 4; }
  static get COL_IS_ACCOUNT() { return 5; }
  static get COL_IS_BUDGET() { return 6; }
  static get SHEET_NAME() { return 'Spreadsheet summary'; }
  constructor() {
    logWithTimeInterval(getLineNumber())
    this.sheet = new IswSheet(SpreadsheetSummary.SHEET_NAME);

    logIt(`1358: Initialized sheet: ${this.getSheetName()}`);
  }

  getAccountSheetNames() {
    logWithTimeInterval(getLineNumber())
    const accountSheetNames = [];
    const dataRange = this.sheet.getDataRange().offset(1, 0);
    logWithTimeInterval(getLineNumber())
    const data = dataRange.getValues();
    logWithTimeInterval(getLineNumber())
    data.forEach(row => {
      if (row[SpreadsheetSummary.COL_IS_ACCOUNT]) {
        accountSheetNames.push(row[SpreadsheetSummary.COL_SHEET_NAME]);
      }
    });

    return accountSheetNames;
  }

  getBudgetSheetNames() {
    const budgetSheetNames = [];
    const dataRange = this.sheet.getDataRange().offset(1, 0);
    const data = dataRange.getValues();
    data.forEach(row => {
      if (row[SpreadsheetSummary.COL_IS_BUDGET]) {
        budgetSheetNames.push(row[SpreadsheetSummary.COL_SHEET_NAME]);
      }
    });
    Logger.log(budgetSheetNames);

    return budgetSheetNames;
  }

  getSheet() {
    return this.sheet;
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  getSheetNames() {
    const sheetNames = [];
    const dataRange = this.sheet.getDataRange().offset(1, 0);
    const data = dataRange.getValues();
    data.forEach(row => {
      sheetNames.push(row[SpreadsheetSummary.COL_SHEET_NAME]);
    });

    return sheetNames;
  }

  update() {
    // Step 1: Collect sheet data
    const iswSheets = iswActiveSpreadsheet.getSheets();
    const sheetData = iswSheets.map(iswSheet => (
      {
        sheetName: iswSheet.getSheetName(),
        lastRow: iswSheet.getLastRow(),
        lastColumn: iswSheet.getLastColumn(),
        maxRows: iswSheet.getMaxRows(),
        maxColumns: iswSheet.getMaxColumns(),
        isAccount: iswSheet.getSheetName().startsWith('_'),
        isBudget: iswSheet.getSheetName().startsWith('Budget')
      }
    ));

    sheetData.unshift({
      sheetName: 'Sheet names',
      lastRow: 'Last row',
      lastColumn: 'Last column',
      maxRows: 'Max rows',
      maxColumns: 'Max columns',
      isAccount: 'Account?',
      isBudget: 'Budget?'
    });

    logIt(sheetData);  // Logging the collected sheet data

    // Step 2: Transform the sheet data into an array suitable for setValues
    const sheetArray = sheetData.map((sheet, row) => {
      const rowArray = [];
      rowArray[SpreadsheetSummary.COL_SHEET_NAME] = sheet.sheetName;
      rowArray[SpreadsheetSummary.COL_LAST_ROW] = sheet.lastRow;
      rowArray[SpreadsheetSummary.COL_LAST_COL] = sheet.lastColumn;
      rowArray[SpreadsheetSummary.COL_MAX_ROWS] = sheet.maxRows;
      rowArray[SpreadsheetSummary.COL_MAX_COLS] = sheet.maxColumns;
      rowArray[SpreadsheetSummary.COL_IS_ACCOUNT] = sheet.isAccount;
      rowArray[SpreadsheetSummary.COL_IS_BUDGET] = sheet.isBudget;
      return rowArray;
    });

    logIt(sheetArray);  // Logging the transformed sheet array

    // Step 3: Determine the maximum row length
    const maxWidth = Math.max(
      ...sheetArray.map(row => row.length)
    );

    // Step 4: Clear the sheet and set the values
    this.sheet.clear();
    const range = this.sheet.getRange(1, 1, sheetArray.length, maxWidth);
    range.setValues(sheetArray);
    this.sheet.activate();
  }

}

const IswLog = class {
  constructor(message) {
    this.message = message;
  }

  commit() {
    Logger.log(this.message);
  }
}

const logIt = (message) => {
  const iswLog = new IswLog(message);
  iswLog.commit();
}

function applyDescriptionReplacements() {
  Logger.log(`applyDescriptionReplacements started`);
  const activeSheet = iswActiveSpreadsheet.getActiveSheet();
  const accountSheet = new AccountSheet(activeSheet);
  if (accountSheet) {
    accountSheet.applyDescriptionReplacements();
  }
  Logger.log(`applyDescriptionReplacements finished`);
}

function balanceSheet() {
  const balanceSheet = new BalanceSheet();

  balanceSheet.setActiveCell("A1");
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
  goToSheet('Budget predicted spend');
}

function budgetWeeklyTransactions() {
  goToSheet('Budget weekly transactions');
}

function checkDependencies() {
  const dependencies = new Dependencies();
  dependencies.updateAllDependencies();
}

function checkFixedAmounts(e) {
  const ourFinances = new OurFinances()
  ourFinances.checkFixedAmounts()
}

function cloneDate(date) {
  return new Date(date.getTime())
}

function convertCurrentColumnToUppercase() {
  const sheet = gasSpreadsheetApp.getActiveSheet();
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
    gasSpreadsheetApp.getUi().alert('No account sheets found!');
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
  Logger.log('createGasMenu started')
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
    ['Update spreadsheet summary', 'updateSpreadsheetSummary'],
  ]
  createUiMenu('GAS Menu', itemArray)
  Logger.log('createGasMenu finished')
}

function createSectionsMenu() {
  Logger.log('createSectionsMenu started')

  /*
    const budgetSheetNames = listSheetNames('budget');
  
    const budgetSheetNamesMap = budgetSheetNames.map(sheetName => toValidFunctionName(sheetName));
    Logger.log(budgetSheetNamesMap);
    return;
  */

  const ui = gasSpreadsheetApp.getUi();
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

  Logger.log('createSectionsMenu finished')
}

function createUiMenu(menuCaption, menuItemArray) {
  const ui = gasSpreadsheetApp.getUi();
  const menu = ui.createMenu(menuCaption);

  menuItemArray.forEach(([itemName, itemFunction]) => {
    menu.addItem(itemName, itemFunction);
  });

  menu.addToUi();
}

function dailySorts() {
  const spreadsheet = gasActiveSpreadsheet;
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
  const bankAccounts = new BankAccounts();
  bankAccounts.showDaily();
}

function emailUpcomingPayments() {
  const ourFinances = new OurFinances();
  ourFinances.emailUpcomingPayments();
}

function examineObject(object, name = 'anonymous value') {
  Logger.log(`${name} has type ${getType(object)}`);

  if (typeof object === 'object' && object !== null) {
    const keys = Object.keys(object);
    Logger.log('Object.keys: ' + JSON.stringify(keys));

    const ownPropertyNames = Object.getOwnPropertyNames(object);
    Logger.log('Object.getOwnPropertyNames: ' + JSON.stringify(ownPropertyNames));

    // Get own properties
    const ownDescriptors = Object.getOwnPropertyDescriptors(object);
    Logger.log('Object.getOwnPropertyDescriptors: ' + JSON.stringify(ownDescriptors));

    // Get prototype properties (including greet)
    const prototypeDescriptors = Object.getOwnPropertyDescriptors(Object.getPrototypeOf(object));
    Logger.log('Prototype descriptors: ' + JSON.stringify(prototypeDescriptors));
  }
}

const findAllNamedRangeUsage = () => {
  const sheets = gasActiveSpreadsheet.getSheets();
  const namedRanges = gasActiveSpreadsheet.getNamedRanges();
  const rangeUsage = [];

  if (!namedRanges.length) {
    Logger.log('No named ranges found in this spreadsheet.');
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
              const cellRef = sheet.getRange(rowIndex + 1, colIndex).getA1Notation();
              rangeUsage.push(`Sheet: ${sheet.getName()} - Cell: ${cellRef} - Name: ${name}`);
            }
          });
        }
      });
    });
  });

  if (rangeUsage.length > 0) {
    Logger.log('Named range(s) found in the following cells:');
    Logger.log(rangeUsage.join('\n'));
  } else {
    Logger.log('No named ranges found in any formulas.');
  }
};

const findNamedRangeUsage = () => {
  findUsageByNamedRange("BRIAN_HALIFAX_BALANCE")
}

const findUsageByNamedRange = (namedRange) => {
  const sheets = gasActiveSpreadsheet.getSheets();
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
    Logger.log(`Named range '${namedRange}' found in the following cells:`);
    Logger.log(rangeUsage.join("\n"));
  } else {
    Logger.log(`Named range '${namedRange}' not found in any formulas.`);
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
  const lastColumn = sheet.getLastColumn(); //Logger.log(lastColumn);
  const firstRowRange = sheet.getRange(1, 1, 1, lastColumn); Logger.log(firstRowRange);
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
    Logger.log(`myEmailAddress: ${myEmailAddress}`);
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
  Logger.log('listPrivateData started');

  const privateDataId = '1hxcINN1seSzn-sLPI25KmV9t4kxLvZlievc0X3EgMhs';
  const sheet = gasSpreadsheetApp.openById(privateDataId);

  if (!sheet) {
    Logger.log("Sheet 'Private Data' not found");
    return;
  }

  // Get data from sheet without header row
  const values = sheet.getDataRange().getValues().slice(1);

  if (values.length === 0) {
    Logger.log('Sheet is empty');
    return;
  }

  let keyValuePairs = {};

  values.forEach(([key, value]) => {
    if (key && value) {
      Logger.log(`key: ${key}, value: ${value}`);
      if (key && value) {
        keyValuePairs[key] = value; // Store the key-value pair in the object
      }
    } else {
      Logger.log(`Invalid key-value pair: key=${key}, value=${value}`);
    }
  });
  Logger.log(keyValuePairs);

  Logger.log('listPrivateData finished');

  return keyValuePairs;
}

function getReplacementHeadersMap() {
  const spreadsheet = gasActiveSpreadsheet;
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

function getSeasonName(date) {
  const seasons = ['Winter', 'Spring', 'Summer', 'Autumn'];

  const monthSeasons = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0];

  const monthIndex = getMonthIndex(date);
  const seasonIndex = monthSeasons[monthIndex];

  return seasons[seasonIndex];
}

function getToday(options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) {
  const date = new Date();
  const locale = getLocale();
  let today;

  try {
    const dtf = new Intl.DateTimeFormat(locale, options);
    today = dtf.format(date);
  } catch (error) {
    Logger.log(`Error formatting date: ${error.message}`);
    today = date.toLocaleDateString(locale, options); // Fallback to toLocaleDateString
  }

  return today;
}

function getType(value) {
  if (value === null) {
    return "null";
  }
  const baseType = typeof value;
  // Primitive types
  if (!["object", "function"].includes(baseType)) {
    return baseType;
  }

  // Symbol.toStringTag often specifies the "display name" of the
  // object's class. It's used in Object.prototype.toString().
  const tag = value[Symbol.toStringTag];
  if (typeof tag === "string") {
    return tag;
  }

  // If it's a function whose source code starts with the "class" keyword
  if (
    baseType === "function" &&
    Function.prototype.toString.call(value).startsWith("class")
  ) {
    return "class";
  }

  // The name of the constructor; for example `Array`, `GeneratorFunction`,
  // `Number`, `String`, `Boolean` or `MyCustomClass`
  const className = value.constructor.name;
  if (typeof className === "string" && className !== "") {
    return className;
  }

  // At this point there's no robust way to get the type of value,
  // so we use the base implementation.
  return baseType;
}

function goToSheet(sheetName) {
  Logger.log(`goToSheet started`);
  // Get the spreadsheet object.
  const spreadsheet = gasActiveSpreadsheet;

  // Get the sheet by name.
  const sheet = new IswSheet(spreadsheet.getSheetByName(sheetName));
  Logger.log(`sheetName: ${sheet.sheetName}`);

  // Check if the sheet exists before trying to activate it.
  if (sheet) {
    sheet.activate();
  } else {
    Logger.log('Sheet not found: ' + sheetName);
  }
  Logger.log(`goToSheet finished`);
}

function goToSheetLastRow(sheetName) {
  Logger.log(`goToSheetLastRow started`);

  // Get the sheet by name and activate it.
  const sheet = new IswSheet(gasActiveSpreadsheet.getSheetByName(sheetName));
  Logger.log(`sheet.getSheetName(): ${sheet.getSheetName()}`);

  // Get the last row with content
  const lastRow = sheet.getLastRow();

  // Get the first cell in the last row (Column A)
  const cell = sheet.getRange(lastRow, 1);

  // Activate the cell
  sheet.setActiveRange(cell);

  const accountSheet = new AccountSheet(sheet);
  accountSheet.analyzeSheet();
  Logger.log(`goToSheetLastRow finished`);
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

const isAccountSheet = (sheet) => {
  if (sheet.getSheetName().startsWith('_')) return true;
  return false;
}

function isCellAccountBalance(sheet, column) {
  const accountBalance = "Account Balance";

  let isCellAccountBalance = false;

  const firstRowRange = getFirstRowRange(sheet);

  const values = firstRowRange.getValues()
  for (const row in values) {
    const cell = values[row][column - 1];
    Logger.log(cell);

    newCell = cell.replace(/\n/g, " ");
    Logger.log(newCell);

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
    Logger.log("Cell contains a valid date.");
    return true;
  } else {
    Logger.log("Cell does NOT contain a date.");
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

  logWithTimeInterval(getLineNumber())
  const spreadsheetSummary = new SpreadsheetSummary();

  logWithTimeInterval(getLineNumber())
  // Process based on sheetNameType
  switch (sheetNameType) {
    case 'account':
      return spreadsheetSummary.getAccountSheetNames();

    case 'all':
      // Return all sheet names
      return spreadsheetSummary.getSheetNames();

    case 'budget':
      return spreadsheetSummary.getBudgetSheetNames();

    default:
      throw new Error(`Unexpected sheetNameType: ${sheetNameType}`);
  }
}

function mergeTransactions() {
  const { getSheetByName } = gasActiveSpreadsheet;

  // Destructuring to cleanly get sheets
  const transactionsBuilderSheet = getSheetByName("Transactions Builder");

  if (!transactionsBuilderSheet) {
    Logger.log("Sheet 'Transactions Builder' not found");
    return;
  }

  const transactionsSheet = getSheetByName("Transactions");

  if (!transactionsSheet) {
    Logger.log("Sheet 'Transactions' not found");
    return;
  }

  // Batch getting the formula values from the "Transactions Builder" sheet
  const formulas = transactionsBuilderSheet.getRange("G3:G4").getValues();

  // Logging both formulas
  Logger.log(`keyFormula: =${formulas[0][0]}`);
  Logger.log(`secondFormula: =${formulas[1][0]}`);

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
  logWithTimeInterval('onEdit started')
  setLastUpdatedOnAccountBalanceChange(e);
  checkFixedAmounts(e)
}

function onOpen() {
  const spreadsheet = iswActiveSpreadsheet;

  // Displaying a temporary notification to the user
  spreadsheet.toast("Please wait while I do a few tasks", "Please wait!", 500);

  // Calling custom menu creation functions
  createAccountsMenu();
  createGasMenu();
  createSectionsMenu();

  // Notifying the user that the tasks are finished
  spreadsheet.toast("You can do your thing now.", "I'm finished!", 3);
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

const findRowByKey = (sheetName, keyColumn, keyValue) => {
  const sheet = gasActiveSpreadsheet.getSheetByName(sheetName);
  const data = sheet.getRange(`${keyColumn}1:${keyColumn}${sheet.getLastRow()}`).getValues();

  const rowIndex = data.findIndex(row => row[0] === keyValue);
  return rowIndex !== -1 ? rowIndex + 1 : -1; // Add 1 for 1-based indexing, return -1 if not found
};

function setLastUpdatedOnAccountBalanceChange(e) {
  logWithTimeInterval('setLastUpdatedOnAccountBalanceChange started')
  const range = e.range;

  const sheet = range.getSheet();

  if (isAccountSheet(sheet)) {
    const bankAccounts = new BankAccounts();

    const key = sheet.getSheetName().slice(1);

    bankAccounts.updateLastUpdatedByKey(key);
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
  const spreadsheet = gasActiveSpreadsheet;

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
    Logger.log("Sheet: " + sheetName + " has " + lastRow + " rows.");

    // Optionally, display in a message box
    // Browser.msgBox("Sheet: " + sheetName + " has " + lastRow + " rows.");
  }
}

function showTransactionsBuilderSteps() {
  // Get the active spreadsheet
  const spreadsheet = gasActiveSpreadsheet;

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
      Logger.log("Sheet: " + sheetName + " has " + lastRow + " rows.");

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
  const ss = gasActiveSpreadsheet;

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

const toValidFunctionName = (str) => {
  // Remove non-alphanumeric characters, except for letters and digits, replace them with underscores
  let validName = str.trim().replace(/[^a-zA-Z0-9]/g, '_');

  // Ensure the name starts with a letter or underscore
  return /^[a-zA-Z_]/.test(validName) ? validName : `_${validName}`;
};

function trimGoogleSheet(iswSheet) {
  let sheet;
  if (iswSheet) {
    sheet = iswSheet;
  } else {
    sheet = iswActiveSpreadsheet.getActiveSheet();
  }

  sheet.trimSheet();
}

function trimGoogleSheets() {
  const spreadsheet = gasActiveSpreadsheet;

  const sheets = spreadsheet.getSheets();
  sheets.forEach(sheet => {
    sheet.trimSheet();
  });
}

function updateSpreadsheetSummary() {
  const spreadsheetSummary = new SpreadsheetSummary();
  spreadsheetSummary.update();
  trimGoogleSheet(spreadsheetSummary.getSheet());
}

/**
 * Custom XLOOKUP function for Google Apps Script
 * 
 * @param {string|number} searchValue - The value you are searching for.
 * @param {Sheet} sheet - The sheet where the lookup is performed.
 * @param {string} searchCol - The column letter to search in (e.g., 'A').
 * @param {string} resultCol - The column letter for the result (e.g., 'B').
 * @param {boolean} [exactMatch=true] - Whether to look for exact matches.
 * @returns {string|number|null} The result of the lookup or null if not found.
 */
function xLookup(searchValue, sheet, searchCol, resultCol, exactMatch = true) {
  const searchRange = sheet.getRange(`${searchCol}1:${searchCol}`).getValues();
  const resultRange = sheet.getRange(`${resultCol}1:${resultCol}`).getValues();

  for (let i = 0; i < searchRange.length; i++) {
    const cellValue = searchRange[i][0];

    // Handle exact or approximate match cases
    if ((exactMatch && cellValue === searchValue) ||
      (!exactMatch && cellValue.toString().toLowerCase().includes(searchValue.toString().toLowerCase()))) {
      return resultRange[i][0];  // Return the corresponding result value
    }
  }

  Logger.log(`Value '${searchValue}' not found in column ${searchCol}`);
  return null;  // Return null if no match is found
}

function getLineNumber() {
  try {
    throw new Error();
  } catch (e) {
    // Extract line number from the stack trace
    const stack = e.stack.split('\n');
    const line = stack[2].match(/:(\d+):\d+\)?$/);
    return line ? line[1] : 'unknown';
  }
}

function logWithTimeInterval(message) {
  const time = new Date().getTime();
  const timeDiffMs = time - previousTime;
  Logger.log(`After ${timeDiffMs} milleseconds - ${message}`);
  previousTime = time;
}
let previousTime = new Date().getTime();



logWithTimeInterval(getLineNumber());
const gasSpreadsheetApp = SpreadsheetApp;
logWithTimeInterval(getLineNumber());
const gasActiveSpreadsheet = gasSpreadsheetApp.getActiveSpreadsheet();
const iswActiveSpreadsheet = new IswSpreadsheet();
logWithTimeInterval(getLineNumber())

const accountSheetNames = listSheetNames('account');
logWithTimeInterval(getLineNumber())

accountSheetNames.forEach(sheetName => {
  const funName = `dynamicAccount${sheetName}`;
  this[funName] = () => goToSheetLastRow(sheetName);
});

logWithTimeInterval(getLineNumber())