/* function logWithTimeInterval requires previousTime to be defined before being used */
let previousTime = new Date().getTime();
logWithTimeInterval(`# ${getLineNumber()} Processing Code.gs`);

// Class declarations

class AccountSheet {
  static get COLUMNS() {
    return {
      DATE: 1,
      DESCRIPTION: 2,
      CREDIT: 3,
      DEBIT: 4,
      NOTE: 5,
      COUNTERPARTY: 6,
      COUNTERPARTY_DATE: 7,
      BALANCE: 8,
    };
  };

  static get ROW_DATA_STARTS() { return 2; }

  static get HEADERS() {
    return ['Date', 'Description', 'Credit (£)', 'Debit (£)', 'Note', 'CPTY', 'Date CPTY', 'Balance (£)'];
  }

  static get MINIMUM_COLUMNS() { return 8; }

  constructor(iswSheet) {
    if (iswSheet) {
      const sheetName = iswSheet.getSheetName();
      if (sheetName[0] === '_') {
        // Logger.log(`${sheetName} is an account sheet`);
        this.sheet = iswSheet;
      } else {
        throw new Error(`${sheetName} is NOT an account sheet`);
      }
    }
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

  formatSheet() {
    try {
      this.validateSheet();
      this.setSheetFormatting();
      this.addDefaultNotes();
      this.convertColumnToUppercase(AccountSheet.COLUMNS.DESCRIPTION);
      this.convertColumnToUppercase(AccountSheet.COLUMNS.NOTE);
      this.setColumnWidth(AccountSheet.COLUMNS.DESCRIPTION, 500);
      this.setColumnWidth(AccountSheet.COLUMNS.NOTE, 170);
    } catch (error) {
      this.log(`Error formatting sheet: ${error.message}`, 'error');
      throw error;
    }
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
    });
  }

  get spreadsheet() {
    return this.sheet.spreadsheet;
  }

  get spreadsheetName() {
    return this.sheet.spreadsheetName;
  }

  getExpectedHeader(column) {
    return column === AccountSheet.COLUMNS.DESCRIPTION
      ? this.xLookup(this.getSheetName().slice(1), this.sheet.getParent().getSheetByName(BankAccounts.SHEET.NAME), 'A', 'AQ')
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

  setCounterpartyValidation(a1range) {
    const range = this.sheet.getRange(a1range);
    const validationRange = `'${BankAccounts.SHEET.NAME}'!$A$2:$A`;
    const rule = gasSpreadsheetApp.newDataValidation()
      .requireValueInRange(this.sheet.getParent().getRange(validationRange), true)
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

  /* Background colour can be cyan */
  setSheetFont(fontFamily = 'Arial', fontSize = 10, fontColor = '#000000') {
    const range = this.sheet.getDataRange();
    range
      .setFontFamily(fontFamily)
      .setFontSize(fontSize)
      .setFontColor(fontColor);
    this.log('Set sheet font to ${fontFamily}, size ${fontSize}, colour ${fontColor}');
  }

  setSheetFormatting() {
    const sheet = this.sheet;
    const dataRange = sheet.getDataRange();

    dataRange.clearDataValidations();

    // Apply formatting in batches
    const headerRange = sheet.getRange(1, 1, 1, AccountSheet.MINIMUM_COLUMNS);
    headerRange
      .setFontWeight('bold')
      .setHorizontalAlignment('left');

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

class BankAccounts {
  static get COLUMNS() {
    return {
      KEY: 1,
      OWNER_CODE: 3,
      CHECK_BALANCE_FREQUENCY: 12,
      BALANCE_UPDATED: 19,
      KEY_LABEL: 'A'
    }
  };
  static get OWNER_CODES() {
    return {
      BRIAN: 'A',
      CHARLIE: 'C',
      LINDA: 'L'
    }
  };
  static get SHEET() { return { NAME: 'Bank accounts' } };

  constructor() {
    this.sheet = new Sheet(BankAccounts.SHEET.NAME);

    if (!this.sheet) {
      throw new Error(`Sheet '${BankAccounts.SHEET.NAME}' not found.`);
    }
  }

  applyFilters(filters) {
    const sheet = this.sheet;

    // Clear any existing filters
    this.removeFilter();

    const filter = sheet.getDataRange().createFilter();

    filters.forEach(item => {
      const criteria = item.hideValues === null
        ? activeSpreadsheet.newFilterCriteria().whenCellEmpty().build()
        : activeSpreadsheet.newFilterCriteria().setHiddenValues(item.hideValues).build();

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
    if (level === 'error') {
      // Logger.log(`ERROR: ${logMessage}`);
    } else {
      // Logger.log(logMessage);
    }
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
    const colCheckBalanceFrequency = BankAccounts.COLUMNS.CHECK_BALANCE_FREQUENCY;
    const colOwnerCode = BankAccounts.COLUMNS.OWNER_CODE;
    const hideOwnerCodes = [
      BankAccounts.OWNER_CODES.BRIAN,
      BankAccounts.OWNER_CODES.CHARLIE,
      BankAccounts.OWNER_CODES.LINDA,
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
    const row = findRowByKey(BankAccounts.SHEET.NAME, BankAccounts.COLUMNS.KEY_LABEL, key);
    // this.log(`row: ${row}`);

    const lastUpdateCell = this.sheet.getRange(row, BankAccounts.COLUMNS.BALANCE_UPDATED);
    lastUpdateCell.setValue(new Date());
  }

  updateLastUpdatedBySheet(sheet) {
    if (isAccountSheet(sheet)) {
      const key = sheet.getSheetName().slice(1);
      this.updateLastUpdatedByKey(key);
    }
  }
}

class BankDebitsDue {
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

class BudgetAnnualTransactions {
  static get COLUMNS() {
    return {
      DATE: 0,
      DESCRIPTION: 1,
      CHANGE_AMOUNT: 3,
      FROM_ACCOUNT: 4,
      PAYMENT_TYPE: 5
    }
  };
  static get SHEET() {
    return {
      NAME: 'Budget annual transactions'
    }
  }

  constructor(ourFinances) {
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName(BudgetAnnualTransactions.SHEET.NAME);
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
        [BudgetAnnualTransactions.COLUMNS.DATE]: date,
        [BudgetAnnualTransactions.COLUMNS.CHANGE_AMOUNT]: changeAmount,
        [BudgetAnnualTransactions.COLUMNS.DESCRIPTION]: description,
        [BudgetAnnualTransactions.COLUMNS.FROM_ACCOUNT]: fromAccount,
        [BudgetAnnualTransactions.COLUMNS.PAYMENT_TYPE]: paymentType
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

class BudgetMonthlyTransactions {
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

class BudgetAdhocTransactions {
  static get COL_CHANGE_AMOUNT() { return 3; }
  static get COL_DATE() { return 0; }
  static get COL_DESCRIPTION() { return 1; }
  static get COL_FROM_ACCOUNT() { return 6; }
  static get COL_PAYMENT_TYPE() { return 7; }

  constructor(ourFinances) {
    this.spreadsheet = ourFinances.spreadsheet;
    this.sheet = this.spreadsheet.getSheetByName('Budget ad hoc transactions');
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

    upcomingPayments += '\nAd hoc payment(s) due:\n';

    // Iterate over transactions and filter valid ones
    scheduledTransactions.forEach(transaction => {
      const changeAmount = transaction[BudgetAdhocTransactions.COL_CHANGE_AMOUNT];
      const transactionDate = transaction[BudgetAdhocTransactions.COL_DATE];

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
        return `\t${getOrdinalDate(day.date)} ${getAmountAsGBP(changeAmount)} from ${transaction[BudgetAdhocTransactions.COL_FROM_ACCOUNT]} by ${transaction[BudgetAdhocTransactions.COL_PAYMENT_TYPE]} ${transaction[BudgetAdhocTransactions.COL_DESCRIPTION]}\n`;
      }
      day = days.next();
    }

    return null;
  }
}

class BudgetWeeklyTransactions {
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
        // Logger.log(`daySelected: ${daySelected}`)

        const formattedDaySelected = getFormattedDate(new Date(daySelected), "GMT+1", "dd/MM/yyyy")
        // Logger.log(`formattedDaySelected: ${formattedDaySelected}`)

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

class CheckFixedAmounts {
  // Column definitions using static getters
  static get COLUMNS() {
    return {
      TAX_YEAR: 0,
      CATEGORY: 1,
      FIXED_AMOUNT: 2,
      DYNAMIC_AMOUNT: 3,
      TOLERANCE: 4,
      MISMATCH: 5
    };
  };

  // Sheet configuration using static getters
  static get SHEET() {
    return {
      NAME: 'Check fixed amounts',
      MIN_COLUMNS: 6,  // Minimum expected columns
      HEADER_ROW: 1    // Number of header rows to skip
    };
  };

  /**
   * Creates an instance of CheckFixedAmounts.
   * @throws {Error} If sheet cannot be found or initialized
   */
  constructor() {
    try {
      this.sheet = new Sheet(CheckFixedAmounts.SHEET.NAME);
      this.validateSheetStructure();
    } catch (error) {
      // Logger.log(`Failed to initialize CheckFixedAmounts: ${error.message}`);
      throw new Error(`Sheet initialization failed: ${error.message}`);
    }
  }

  /**
     * Creates a mismatch message for a row
     * @private
     * @param {Array<any>} row - The row data
     * @return {string} Formatted mismatch message
     */
  createMismatchMessage(row) {
    const columns = CheckFixedAmounts.COLUMNS;

    return Utilities.formatString(
      '%s %s: Dynamic amount (%s) does not match fixed amount (%s)',
      row[columns.TAX_YEAR],
      row[columns.CATEGORY],
      getAmountAsGBP(row[columns.DYNAMIC_AMOUNT]),
      getAmountAsGBP(row[columns.FIXED_AMOUNT])
    );
  }

  getEmailBody() {
    return this.getMismatches().join(`\n`);
  }

  /**
     * Retrieves values from the sheet with caching
     * @private
     * @return {Array<Array<any>>} Sheet values
     * @throws {Error} If unable to get sheet values
     */
  getValues() {
    try {
      // Cache the values if not already cached
      if (!this.cachedValues) {
        const range = this.sheet.getDataRange();
        if (!range) {
          throw new Error('Could not get data range from sheet');
        }
        this.cachedValues = range.getValues();
      }
      return this.cachedValues;
    } catch (error) {
      // Logger.log(`Failed to get sheet values: ${error.message}`);
      throw new Error(`Could not retrieve sheet data: ${error.message}`);
    }
  }

  getMismatchMessages() {
    const mismatches = [];
    let mismatchMessages = [];
    const values = this.getValues();

    // Start after header row
    for (let i = CheckFixedAmounts.SHEET.HEADER_ROW; i < values.length; i++) {
      const row = values[i];

      // Skip invalid rows
      if (!this.isValidRow(row)) {
        mismatches.push({
          rowNumber: i + 1,
          message: `CheckFixedAmounts: Skipping invalid row`
        });
        continue;
      }

      if (row[CheckFixedAmounts.COLUMNS.MISMATCH] === 'Mismatch') {
        mismatches.push({
          rowNumber: i + 1,
          message: this.createMismatchMessage(row)
        });
      }
    };
    if (mismatches.length > 0) {
      mismatchMessages = mismatches
        .map(function (m) {
          return 'Row ' + m.rowNumber + ': ' + m.message;
        })
    }
    return mismatchMessages;
  }

  /**
     * Validates a single row of data
     * @private
     * @param {Array<any>} row - The row to validate
     * @return {boolean} Whether the row is valid
     */
  isValidRow(row) {
    const columns = CheckFixedAmounts.COLUMNS;

    return Boolean(
      row &&
      row.length >= CheckFixedAmounts.SHEET.MIN_COLUMNS &&
      row[columns.CATEGORY] &&
      !isNaN(Number(row[columns.DYNAMIC_AMOUNT])) &&
      !isNaN(Number(row[columns.FIXED_AMOUNT]))
    );
  }

  /**
   * Validates the basic structure of the sheet
   * @private
   * @throws {Error} If sheet structure is invalid
   */
  validateSheetStructure() {
    const values = this.getValues();

    if (!values || !Array.isArray(values) || values.length <= CheckFixedAmounts.SHEET.HEADER_ROW) {
      throw new Error('Sheet is empty or contains insufficient data');
    }

    if (values[0].length < CheckFixedAmounts.SHEET.MIN_COLUMNS) {
      throw new Error(`Sheet must have at least ${CheckFixedAmounts.SHEET.MIN_COLUMNS} columns`);
    }
  }
}

class Dependencies {
  static get SHEET_NAME() { return 'Dependencies'; }
  constructor() {
    this.sheet = new Sheet(Dependencies.SHEET_NAME);
  }

  getAllDependencies() {
    // Logger.log("Dependencies.getAllDependencies");

    if (typeof this.allDependencies !== 'undefined') {
      // Logger.log(`getAllDependencies: using cached dependencies: ${this.allDependencies}`);
      return this.allDependencies;
    }

    // Retrieve dependencies if not cached
    let allDependencies = this.getSheet().getDataRange().getValues();

    // Remove the first row (header or irrelevant row)
    allDependencies.shift();

    // Cache the result for future use
    this.allDependencies = allDependencies;

    // Logger.log(`getAllDependencies: freshly loaded dependencies: ${allDependencies}`);

    return allDependencies;
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }

  getSpreadsheetNameById(spreadsheetId) {
    try {
      const spreadsheet = new Spreadsheet(spreadsheetId);
      return spreadsheet.spreadsheetName;
    } catch (error) {
      // Logger.log(`Error fetching spreadsheet with ID: ${spreadsheetId}. ${error.message}`);
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

class DescriptionReplacements {
  static get SHEET_NAME() { return 'Description replacements'; }

  constructor() {
    this.sheet = new Sheet(DescriptionReplacements.SHEET_NAME);
  }

  applyReplacements(accountSheet) {
    const accountSheetName = accountSheet.sheetName;
    if (accountSheetName === this.getSheetName()) {
      throw new Error(`Cannot applyDescriptionReplacements to '${accountSheetName}'`);
    }

    const headerValue = accountSheet.getRange(1, AccountSheet.COLUMNS.DESCRIPTION).getValue();
    if (!headerValue.startsWith("Description")) {
      throw new Error(`Unexpected description header '${headerValue}' in sheet: ${accountSheetName}`);
    }

    const lastRow = accountSheet.getLastRow();
    const numRows = lastRow + 1 - AccountSheet.ROW_DATA_STARTS;

    const range = accountSheet.getRange(AccountSheet.ROW_DATA_STARTS, AccountSheet.COLUMNS.DESCRIPTION, numRows, 1);
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
      // Logger.log(`Updated ${numReplacements} values in sheet: ${accountSheetName}`);
    } else {
      // Logger.log(`No replacements made in sheet: ${accountSheetName}`);
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
    if (level === 'error') {
      // Logger.log(`ERROR: ${logMessage}`);
    } else {
      // Logger.log(logMessage);
    }
  }
}

class HMRC_S {
  // Column definitions using static getters
  static get COLUMNS() {
    return {
      QUESTIONS: 0,
      CATEGORY: 1,
      LATEST_TAX_YEAR: 2,
    };
  }

  // Sheet configuration using static getters
  static get SHEET() {
    return {
      NAME: 'HMRC S',
      HEADER_ROW: 1, // Number of header rows to skip
    };
  }

  // Handles the edit event
  handleEdit(trigger) {
    try {
      const value = trigger.getValue();
      // Logger.log(`value: ${value}`);
      const row = trigger.getRow();
      // Logger.log(`row: ${row}`);
      const column = trigger.getColumn();
      // Logger.log(`column: ${column}`);

      // Exit early if value is empty or row is part of the header
      if (!value || row <= HMRC_S.SHEET.HEADER_ROW) return;

      // Check if the edit occurred in the "CATEGORY" column
      if (column === HMRC_S.COLUMNS.CATEGORY + 1) {
        const sheet = trigger.getSheet();
        const startColLetter = this.columnNumberToLetter(HMRC_S.COLUMNS.LATEST_TAX_YEAR + 1);
        const lastColLetter = this.columnNumberToLetter(sheet.getLastColumn());

        // Construct QUERY formulas
        const queries = this.buildQueries(value, startColLetter, lastColLetter, row);

        // Set the formulas in the target range
        const targetRange = `${startColLetter}${row}:${lastColLetter}${row}`;
        sheet.getRange(targetRange).setValues([queries]);
      }
    } catch (error) {
      console.error('Error handling handleEdit:', error);
    }
  }

  // Build QUERY formulas for the given range
  buildQueries(value, startCol, lastCol, row) {
    const baseQuery = `=IFNA(QUERY(Transactions!$A$2:$Z, `;
    const labelSuffix = ` LABEL SUM(I) ''"), 0.0)`;

    const queries = [];
    for (let col = startCol; col <= lastCol; col = this.nextColumnLetter(col)) {
      const query = `${baseQuery}"SELECT SUM(I) WHERE J='"&$${col}$1&"' AND M='${HMRC_S.SHEET.NAME} ${value}'${labelSuffix}`;
      queries.push(query);
    }
    return queries;
  }

  // Convert column number to letter (e.g., 1 -> A)
  columnNumberToLetter(colNum) {
    let letter = '';
    while (colNum > 0) {
      const mod = (colNum - 1) % 26;
      letter = String.fromCharCode(65 + mod) + letter;
      colNum = Math.floor((colNum - 1) / 26);
    }
    return letter;
  }

  // Calculate the next column letter (e.g., A -> B)
  nextColumnLetter(col) {
    let carry = 1;
    let result = '';
    for (let i = col.length - 1; i >= 0; i--) {
      const code = col.charCodeAt(i) + carry;
      if (code > 90) {
        result = 'A' + result;
        carry = 1;
      } else {
        result = String.fromCharCode(code) + result;
        carry = 0;
      }
    }
    return carry ? 'A' + result : result;
  }
}

class OurFinances {
  constructor() {
    this.spreadsheet = activeSpreadsheet;
  }

  getFixedAmountMismatches() {
    return this.checkFixedAmounts.getMismatchMessages();
  }

  getUpcomingDebits() {
    // Collect upcoming debits from different sources
    return [
      this.bankDebitsDue.getUpcomingDebits(),
      this.budgetAdhocTransactions.getUpcomingDebits(),
      this.budgetAnnualTransactions.getUpcomingDebits(),
      this.budgetMonthlyTransactions.getUpcomingDebits(),
      this.budgetWeeklyTransactions.getUpcomingDebits()
    ];
  }

  get budgetAnnualTransactions() {
    if (typeof this._budgetAnnualTransactions === 'undefined') {
      this._budgetAnnualTransactions = new BudgetAnnualTransactions(this)
    }
    return this._budgetAnnualTransactions
  }

  get budgetAdhocTransactions() {
    if (typeof this._budgetAdhocTransactions === 'undefined') {
      this._budgetAdhocTransactions = new BudgetAdhocTransactions(this)
    }
    return this._budgetAdhocTransactions
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

  get checkFixedAmounts() {
    if (typeof this._checkFixedAmounts === 'undefined') {
      this._checkFixedAmounts = new CheckFixedAmounts(this)
    }
    return this._checkFixedAmounts;
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
    return this.spreadsheet.getName();
  }

  getSheetByName(sheetName) {
    return this.spreadsheet.getSheetByName(sheetName)
  }

  showAllAccounts() {
    this.bankAccounts.showAll()
  }
}

class Sheet {
  constructor(x = null) {
    //logWithTimeInterval(`# ${getLineNumber()}`);
    const xType = getType(x);

    if (xType === 'string') {
      const sheetName = x;
      logWithTimeInterval(`# ${getLineNumber()}`);
      this.sheet = activeSpreadsheet.getSheetByName(sheetName);
      if (!this.sheet) {
        throw new Error(`Sheet with name "${sheetName}" not found`);
      }
      return;
    }
    //logWithTimeInterval(`# ${getLineNumber()}`);
    if (xType === 'Object') {
      const gasSheet = x;
      this.sheet = gasSheet;
      // this.log(`${this.getSheetName()} initialised`);
      return;
    }

    if (x === null) {
      // Logger.log('No input provided, initializing without a sheet');
      this.sheet = activeSpreadsheet.getActiveSheet();
      if (!this.sheet) {
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
      this._spreadsheet = new Spreadsheet(this.sheet.getParent().getId());
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

  clearContents() {
    this.sheet.clearContents();
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

  getDataRange() {
    return this.sheet.getDataRange();
  }

  getFilter() {
    return this.sheet.getFilter()
  }

  getFrozenColumns() {
    return this.sheet.getFrozenColumns()
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

  getName() {
    return this.sheet.getName();
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

  getSheetId() {
    return this.sheet.getSheetId();
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

  setSheetByName(sheetName) {
    this.spreadsheet = activeSpreadsheet;
    this.sheet = activeSpreadsheet.getSheetByName(sheetName);

    if (!this.sheet) {
      throw new Error(`Sheet '${sheetName}' not found.`);
    }

    this.log(`Initialized sheet: ${sheetName}`);
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

class Spreadsheet {
  constructor(spreadsheetId) {
    if (spreadsheetId) {
      // Logger.log(`spreadsheetId: ${spreadsheetId}`);
      try {
        this.spreadsheet = this.openById(spreadsheetId);
      } catch (error) {
        // Logger.log(`Error opening spreadsheet with ID: ${spreadsheetId}. ${error.message}`);
        throw error;
      }
    } else {
      try {
        // logWithTimeInterval(getLineNumber())
        this.spreadsheet = this.getActiveSpreadsheet();
        logWithTimeInterval(`# ${getLineNumber()}`);
      } catch (error) {
        // Logger.log(`Error opening active spreadsheet: ${error.message}`);
        throw error;
      }
    }

    // // Logger.log(`Initialised spreadsheet: ${this.spreadsheetName}`);
  }

  getActiveSpreadsheet() {
    if (!this._activeSpreadsheet) {
      this._activeSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    }
    return this._activeSpreadsheet;
  }

  getActiveSheet() {
    const activeSheet = this.spreadsheet.getActiveSheet();
    examineObject(activeSheet, 'activeSheet');

    const iswActiveSheet = new Sheet(activeSheet);
    examineObject(iswActiveSheet, 'iswActiveSheet');

    return iswActiveSheet;
  }

  getGasSheets() {
    if (!this._gasSheets) {
      logWithTimeInterval(`# ${getLineNumber()}\tFetching GAS sheets...`);

      this._gasSheets = this.spreadsheet.getSheets();

      logWithTimeInterval(`# ${getLineNumber()}\tRetrieved ${this._gasSheets.length} GAS sheets from ${this.spreadsheetName}.`);
    }

    return this._gasSheets;
  }

  getSheetByNameX(sheetName) {
    let sheet;

    try {
      sheet = this.getSheetMap()[sheetName];
      if (!sheet) {
        // Logger.log('Sheet not found: ' + sheetName);
        return;
      }
    } catch (error) {
      // Logger.log('Error accessing sheet: ' + error.message);

    }

    return sheet;
  }

  getSheetByName(sheetName) {
    logWithTimeInterval(`# ${getLineNumber()} Called getSheetByName with sheetName: '${sheetName}'`);
    let sheet;

    try {
      const sheetMap = this.getSheetMap();
      const sheetCount = Object.keys(sheetMap).length;
      logWithTimeInterval(`# ${getLineNumber()} Sheet map initialized with ${sheetCount} entries.`);

      sheet = sheetMap[sheetName];
      logWithTimeInterval(`# ${getLineNumber()} Retrieved sheet: ${sheetName}`);

      if (!sheet) {
        // Logger.log(`Sheet not found: ${sheetName}`);
        return null; // Explicitly return null for missing sheets
      }
    } catch (error) {
      // Logger.log(`Error accessing sheet "${sheetName}": ${error.message}`);
      return null; // Return null in case of errors
    }

    logWithTimeInterval(`# ${getLineNumber()} Successfully retrieved sheet: ${sheetName}`);
    return sheet;
  }

  getSheetMap() {
    if (!this._sheetMap) {
      // Lazily initialize the sheet map only when it's accessed
      const sheets = this.getSheets();

      // Ensure `sheets` is an array before processing
      if (!Array.isArray(sheets)) {
        throw new Error("getSheets() must return an array");
      }

      // Create the sheet map efficiently using Object.fromEntries
      this._sheetMap = Object.fromEntries(
        sheets.map(sheet => [sheet.getName(), sheet])
      );
    }

    return this._sheetMap;
  }

  getSheets() {
    if (!this._sheets) {
      logWithTimeInterval(`# ${getLineNumber()}\tFetching sheets...`);
      this._sheets = this.getGasSheets().map(sheet => new Sheet(sheet));
      logWithTimeInterval(`# ${getLineNumber()}\tRetrieved ${this._sheets.length} sheets.`);
    }
    return this._sheets;
  }

  getSpreadsheetName() {
    return this.spreadsheet.getName();
  }

  getUrl() {
    return this.spreadsheet.getUrl();
  }

  moveActiveSheet(sheetNumber) {
    this.spreadsheet.moveActiveSheet(sheetNumber);
  }

  newFilterCriteria() {
    return gasSpreadsheetApp.newFilterCriteria();
  }

  openById(spreadsheetId) {
    if (!this.spreadsheets[spreadsheetId]) {
      this.spreadsheets[spreadsheetId] = SpreadsheetApp.openById(spreadsheetId);
    }
    return this.spreadsheets[spreadsheetId];
  }

  setActiveSheet(sheet) {
    examineObject(sheet);
    this.spreadsheet.setActiveSheet(sheet.sheet);
  }

  toast(msg, title, timeoutSeconds) {
    this.spreadsheet.toast(msg, title, timeoutSeconds);
  }
}

class SpreadsheetSummary {
  static get COLUMNS() {
    return {
      SHEET_NAME: 0,
      LAST_ROW: 1,
      LAST_COL: 2,
      MAX_ROWS: 3,
      MAX_COLS: 4,
      IS_ACCOUNT: 5,
      IS_BUDGET: 6
    };
  }

  static get SHEET() {
    return {
      NAME: 'Spreadsheet summary'
    };
  }

  constructor() {
    this.sheet = new Sheet(SpreadsheetSummary.SHEET.NAME);
    this.data = this.sheet.getDataRange().offset(1, 0).getValues();
  }

  getAccountSheetNames() {
    return this.data
      .filter(row => row[SpreadsheetSummary.COLUMNS.IS_ACCOUNT])
      .map(row => row[SpreadsheetSummary.COLUMNS.SHEET_NAME]);
  }

  getBudgetSheetNames() {
    return this.data
      .filter(row => row[SpreadsheetSummary.COLUMNS.IS_BUDGET])
      .map(row => row[SpreadsheetSummary.COLUMNS.SHEET_NAME]);
  }

  getSheetNames() {
    return this.data.map(row => row[SpreadsheetSummary.COLUMNS.SHEET_NAME]);
  }

  update() {
    const sheetData = activeSpreadsheet.getSheets().map(iswSheet => ({
      sheetName: iswSheet.getSheetName(),
      lastRow: iswSheet.getLastRow(),
      lastColumn: iswSheet.getLastColumn(),
      maxRows: iswSheet.getMaxRows(),
      maxColumns: iswSheet.getMaxColumns(),
      isAccount: iswSheet.getSheetName().startsWith('_'),
      isBudget: iswSheet.getSheetName().startsWith('Budget')
    }));

    sheetData.unshift({
      sheetName: 'Sheet name',
      lastRow: 'Last row',
      lastColumn: 'Last column',
      maxRows: 'Max rows',
      maxColumns: 'Max columns',
      isAccount: 'Is an account file (starts with underscore)?',
      isBudget: 'Is a budget file (starts with Budget)?'
    });

    const sheetArray = sheetData.map(sheet => [
      sheet.sheetName,
      sheet.lastRow,
      sheet.lastColumn,
      sheet.maxRows,
      sheet.maxColumns,
      sheet.isAccount,
      sheet.isBudget
    ]);

    const maxWidth = sheetArray[0].length;

    // Minimize calls to Google Sheets API by using clearContent instead of clear() if possible.
    this.sheet.clearContents();
    this.sheet.getRange(1, 1, sheetArray.length, maxWidth).setValues(sheetArray);
  }

  getSheet() {
    return this.sheet;
  }

  getSheetName() {
    return this.sheet.getSheetName();
  }
}

class Transactions {
  static get SHEET() {
    return {
      NAME: 'Transactions'
    };
  }

  constructor() {
    this.sheet = new Sheet(Transactions.SHEET.NAME);
  }

  activate() {
    this.sheet.activate();
  }

  evaluateQueryFunction(queryString) {
    const sheet = this.sheet;
    const dataRange = sheet.getDataRange(); // Adjust the range as needed
    const a1range = `Transactions!${dataRange.getA1Notation()}`;
    // Logger.log(a1range);

    // Construct the QUERY formula
    const formula = `=IFNA(QUERY(${a1range}, "${queryString}"), 0.0)`;
    // Logger.log(formula);

    // Add the formula to a temporary cell to evaluate it
    const tempCell = sheet.getRange("Z1");
    tempCell.setFormula(formula);

    // Get the result of the QUERY function
    const result = tempCell.getValue();

    // Clear the temporary cell
    tempCell.clear();

    return result;
  }

  getTotalByYear(where, taxYear) {
    const queryString = `SELECT SUM(I) WHERE J='${taxYear}' AND ${where} LABEL SUM(I) ''`;
    // Logger.log(queryString);
    const result = this.evaluateQueryFunction(queryString);
    // Logger.log(result); // Outputs the result of the query
  }

  updateBuilderFormulas(transactionFormulas) {
    // Validate input and extract formulas
    if (
      !transactionFormulas ||
      typeof transactionFormulas.keyFormula !== "string" ||
      typeof transactionFormulas.valuesFormula !== "string"
    ) {
      throw new Error("Invalid transactionFormulas: Expected an object with 'keyFormula' and 'valuesFormula' as strings.");
    }

    const { keyFormula, valuesFormula } = transactionFormulas;

    // Sanitize formulas if needed (basic example, extend as required)
    const safeKeyFormula = keyFormula.trim();
    const safeValuesFormula = valuesFormula.trim();

    try {
      // Set formulas in a single batch operation
      this.sheet.getRange("A1:B1").setFormulas([
        [`=${safeKeyFormula}`, `=${safeValuesFormula}`]
      ]);

      // Logger.log(`Formulas updated successfully: ${safeKeyFormula}, ${safeValuesFormula}`);
    } catch (error) {
      // Logger.log(`Error updating builder formulas: ${error.message}`);
      throw error; // Re-throw after logging
    }
  }
}

class TransactionsBuilder {
  static get SHEET() {
    return {
      NAME: 'Transactions builder'
    };
  }

  constructor() {
    this.sheet = new Sheet(TransactionsBuilder.SHEET.NAME);
  }

  getTransactionFormulas() {
    try {
      // Retrieve the range values
      const range = this.sheet.getRange("G3:G4");
      const values = range.getValues();

      // Validate the retrieved values
      if (!Array.isArray(values) || values.length !== 2 || values[0].length === 0 || values[1].length === 0) {
        throw new Error("Invalid range data: Expected a 2x1 array with formulas in G3 and G4.");
      }

      const [keyFormulaRow, valuesFormulaRow] = values;
      const keyFormula = keyFormulaRow[0];
      const valuesFormula = valuesFormulaRow[0];

      // Log both formulas for debugging
      // Logger.log(`Retrieved Formulas:\n  Key Formula: =${keyFormula}\n  Values Formula: =${valuesFormula}`);

      return {
        keyFormula,
        valuesFormula
      };
    } catch (error) {
      // Logger.log(`Error in getTransactionFormulas: ${error.message}`);
      throw error; // Re-throw error after logging
    }
  }
}

class Trigger {
  constructor(event) {
    this.event = event;
  }
  getColumn() {
    if (!this._column) {
      this._column = this.getRange().getColumn();
    }
    return this._column;
  }
  getOldValue() {
    if (!this._oldValue) {
      this._oldValue = this.event.oldValue;
    }
    return this._oldValue;
  }
  getRange() {
    if (!this._range) {
      this._range = this.event.range;
    }
    return this._range;
  }
  getRow() {
    if (!this._row) {
      this._row = this.getRange().getRow();
    }
    return this._row;
  }
  getSheet() {
    if (!this._sheet) {
      this._sheet = this.getRange().getSheet();
    }
    return this._sheet;
  }
  getSheetName() {
    if (!this._sheetName) {
      this._sheetName = this.getSheet().getName();
    }
    return this._sheetName;
  }
  getValue() {
    if (!this._value) {
      this._value = this.getRange().getValue();
    }
    return this._value;
  }
}

// Function declarations

function alert(message) {
  SpreadsheetApp.getUi().alert(message);
}

function allAccounts() {
  const ourFinances = new OurFinances()
  ourFinances.showAllAccounts()
}

function applyDescriptionReplacements() {
  // Logger.log(`applyDescriptionReplacements started`);
  const activeSheet = activeSpreadsheet.getActiveSheet();
  const accountSheet = new AccountSheet(activeSheet);
  if (accountSheet) {
    accountSheet.applyDescriptionReplacements();
  }
  // Logger.log(`applyDescriptionReplacements finished`);
}

function balanceSheet() {
  goToSheet('Balance sheet');
}

function budget() {
  goToSheet('Budget')
}

function budgetAnnualTransactions() {
  goToSheet(BudgetAnnualTransactions.SHEET.NAME)
}

function budgetMonthlyTransactions() {
  goToSheet('Budget monthly transactions')
}

function budgetAdhocTransactions() {
  goToSheet('Budget ad hoc transactions')
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

function cloneDate(date) {
  return new Date(date.getTime())
}

function columnNumberToLetter(columnNumber) {
  let dividend = columnNumber;
  let letter = "";
  while (dividend > 0) {
    const modulo = (dividend - 1) % 26;
    letter = String.fromCharCode(65 + modulo) + letter;
    dividend = Math.floor((dividend - modulo) / 26);
  }
  return letter;
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
  // accountSheetNames is defined as a global
  //const accountSheetNames = getSheetNamesByType('account');

  // Check if any accounts are found
  if (accountSheetNames.length === 0) {
    alert('No account sheets found!');
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
  // Logger.log('createGasMenu started')
  const itemArray = [
    ['All accounts', 'allAccounts'],
    ['Apply Description replacements', 'applyDescriptionReplacements'],
    ['Balance sheet', 'balanceSheet'],
    ['Check dependencies', 'checkDependencies'],
    ['Convert current column to uppercase', 'convertCurrentColumnToUppercase'],
    ['Daily update', 'dailyUpdate'],
    ['Format sheet', 'formatSheet'],
    ['Monthly update', 'monthlyUpdate'],
    ['Open accounts', 'openAccounts'],
    ['Sort sheet order', 'sortGoogleSheets'],
    ['Trim all sheets', 'trimGoogleSheets'],
    ['Trim sheet', 'trimGoogleSheet'],
    ['Update spreadsheet summary', 'updateSpreadsheetSummary'],
  ]
  createUiMenu('GAS Menu', itemArray)
  // Logger.log('createGasMenu finished')
}

function createSectionsMenu() {
  const ui = gasSpreadsheetApp.getUi();
  const menu = ui.createMenu('Sections')
    .addSubMenu(ui.createMenu('Budget')
      .addItem('Budget', 'budget')
      .addItem(BudgetAnnualTransactions.SHEET.NAME, 'budgetAnnualTransactions')
      .addItem('Budget monthly transactions', 'budgetMonthlyTransactions')
      .addItem('Budget ad hoc transactions', 'budgetAdhocTransactions')
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
    .addSubMenu(ui.createMenu('HMRC')
      .addItem('HMRC Transactions summary', 'goToSheetHMRCTransactionsSummary')
      .addItem('Self Assessment Ian Bernard', 'goToSheetHMRC_B')
      .addItem('Self Assessment Ian Sweeney', 'goToSheetHMRC_S')
      .addItem('SES Childcare', 'goToSheetHMRCTransactionsSummary')
      .addItem('SES Property management', 'goToSheetHMRCTransactionsSummary')
      .addItem('TR People', 'goToSheetPeople')
      .addItem('UKP Fownes Street', 'goToSheetHMRCTransactionsSummary')
      .addItem('UKP One Park West', 'goToSheetHMRCTransactionsSummary')
    )
    .addSeparator()
    .addSubMenu(ui.createMenu('SW18 3PT')
      .addItem('Home Assistant inventory', 'goToSheetSW183PTInventory')
      .addItem('Inventory', 'goToSheetSW183PTInventory')
    )
    .addSeparator()
    .addItem('Xfers mismatch', 'goToSheetXfersMismatch')
    .addToUi();
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
  const sheetsToSort = [
    BankAccounts.SHEET.NAME,
    BudgetAnnualTransactions.SHEET.NAME,
    "Budget monthly transactions",
    "Budget weekly transactions",
    "Description replacements",
    "Transactions categories",
  ];
  sheetsToSort.forEach(sheetName => {
    const sheet = activeSpreadsheet.getSheetByName(sheetName);
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

function dynamicQuery(rangeString, queryString) {
  try {
    // Import QUERY function from DataTable
    const dataTable = Charts.newDataTable()
      .addColumn('Column', 'string')
      .build();

    rangeString = rangeString.trim();
    queryString = queryString.trim();

    const result = dataTable.applyQuery(rangeString + ',' + queryString);
    return result.toArray();
  } catch (error) {
    console.error('Error in dynamicQuery:', error);
    throw error;
  }
}

function emailLogs() {
  const body = Logger.getLog();
  if (body.length) {
    // Email logs to the person who ran the script.
    const recipient = Session.getActiveUser().getEmail();
    const subject = 'Logs from Our Finances';
    const body = Logger.getLog();
    MailApp.sendEmail(recipient, subject, body);
  }
}

function emailUpcomingPayments() {
  const ourFinances = new OurFinances();
  ourFinances.emailUpcomingPayments();
}

function examineObject(object, name = 'anonymous value') {
  Logger.log(`${name} has type ${getType(object)}`);

  if (typeof object === 'object' && object !== null) {
    const keys = Object.keys(object);
    // Logger.log('Object.keys: ' + JSON.stringify(keys));

    const ownPropertyNames = Object.getOwnPropertyNames(object);
    // Logger.log('Object.getOwnPropertyNames: ' + JSON.stringify(ownPropertyNames));

    // Get own properties
    const ownDescriptors = Object.getOwnPropertyDescriptors(object);
    // Logger.log('Object.getOwnPropertyDescriptors: ' + JSON.stringify(ownDescriptors));

    // Get prototype properties (including greet)
    const prototypeDescriptors = Object.getOwnPropertyDescriptors(Object.getPrototypeOf(object));
    // Logger.log('Prototype descriptors: ' + JSON.stringify(prototypeDescriptors));
  }
}

function findAllNamedRangeUsage() {
  const sheets = activeSpreadsheet.getSheets();
  const namedRanges = activeSpreadsheet.getNamedRanges();
  const rangeUsage = [];

  if (!namedRanges.length) {
    // Logger.log('No named ranges found in this spreadsheet.');
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
    // Logger.log('Named range(s) found in the following cells:');
    // Logger.log(rangeUsage.join('\n'));
  } else {
    // Logger.log('No named ranges found in any formulas.');
  }
}

function findNamedRangeUsage() {
  findUsageByNamedRange("BRIAN_HALIFAX_BALANCE")
}

function findRowByKey(sheetName, keyColumn, keyValue) {
  const sheet = activeSpreadsheet.getSheetByName(sheetName);
  const data = sheet.getRange(`${keyColumn}1:${keyColumn}${sheet.getLastRow()}`).getValues();

  const rowIndex = data.findIndex(row => row[0] === keyValue);
  return rowIndex !== -1 ? rowIndex + 1 : -1; // Add 1 for 1-based indexing, return -1 if not found
}

function findUsageByNamedRange(namedRange) {
  const sheets = activeSpreadsheet.getSheets();
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
    // Logger.log(`Named range '${namedRange}' found in the following cells:`);
    // Logger.log(rangeUsage.join("\n"));
  } else {
    // Logger.log(`Named range '${namedRange}' not found in any formulas.`);
  }
}

function formatSheet() {
  const activeSheet = activeSpreadsheet.getActiveSheet();

  if (!activeSheet) {
    // Logger.log("No active sheet found.");
    return;
  }

  try {
    const accountSheet = new AccountSheet(activeSheet);
    accountSheet.formatSheet();
  } catch (error) {
    // Logger.log(`${activeSheet.sheetName}: ${error.message}`);
  }
}

/**
 * Formats an amount for display as GBP
 * @param {number} amount - The amount to format
 * @return {string} Formatted amount
 */
function getAmountAsGBP(amount) {
  const gbPound = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'GBP',
  });

  return gbPound.format(amount)
}

function getDayName(date) {
  const dayName = date.toLocaleDateString(locale, { weekday: 'long' })
  return dayName
}

// The getDate() method of Date instances returns the day of the month for this date according to local time.
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getDate
function getDayOfMonth(date) {
  return date.getDate()
}

function getDtf() {
  return new Intl.DateTimeFormat(locale);
}

function getFirstRowRange(sheet) {
  const lastColumn = sheet.getLastColumn(); //// Logger.log(lastColumn);
  const firstRowRange = sheet.getRange(1, 1, 1, lastColumn); // Logger.log(firstRowRange);
  return firstRowRange;
}

// https://developers.google.com/apps-script/reference/utilities/utilities#formatDate(Date,String,String)
function getFormattedDate(date, timeZone, format) {
  return Utilities.formatDate(date, timeZone, format)
}

function getHMRCTotalByYear(category, year) {
  return category + '-' + year;
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

function getMonthIndex(date) {
  return date.getMonth();
}

function getMonthName(date) {
  return date.toLocaleDateString(locale, { month: 'long' });
}

function getMyEmailAddress() {
  // Use optional chaining to safely access the email address
  const myEmailAddress = getPrivateData()?.['MY_EMAIL_ADDRESS'];

  // Check if the email address exists and log accordingly
  if (myEmailAddress) {
    // Logger.log(`myEmailAddress: ${myEmailAddress}`);
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

function getPrivateData() {
  // Logger.log('listPrivateData started');

  const privateDataId = '1hxcINN1seSzn-sLPI25KmV9t4kxLvZlievc0X3EgMhs';
  const sheet = gasSpreadsheetApp.openById(privateDataId);

  if (!sheet) {
    // Logger.log("Sheet 'Private Data' not found");
    return;
  }

  // Get data from sheet without header row
  const values = sheet.getDataRange().getValues().slice(1);

  if (values.length === 0) {
    // Logger.log('Sheet is empty');
    return;
  }

  let keyValuePairs = {};

  values.forEach(([key, value]) => {
    if (key && value) {
      // Logger.log(`key: ${key}, value: ${value}`);
      if (key && value) {
        keyValuePairs[key] = value; // Store the key-value pair in the object
      }
    } else {
      // Logger.log(`Invalid key-value pair: key=${key}, value=${value}`);
    }
  });
  // Logger.log(keyValuePairs);

  // Logger.log('listPrivateData finished');

  return keyValuePairs;
}

function getReplacementHeadersMap() {
  const bankAccounts = activeSpreadsheet.getSheetByName(BankAccounts.SHEET.NAME);
  if (!bankAccounts) {
    throw new Error(`Sheet named '${BankAccounts.SHEET.NAME}' not found.`);
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

function getSheetNamesByType(sheetNameType) {
  let sheetNames;
  logWithTimeInterval(`# ${getLineNumber()}`);
  const spreadsheetSummary = new SpreadsheetSummary();
  // Process based on sheetNameType
  switch (sheetNameType) {
    case 'account':
      sheetNames = spreadsheetSummary.getAccountSheetNames();
      break;
    case 'all':
      // Return all sheet names
      sheetNames = spreadsheetSummary.getSheetNames();
      break;
    default:
      throw new Error(`Unexpected sheetNameType: ${sheetNameType}`);
  }
  // Logger.log(`There are ${sheetNames.length} sheets with sheetNameType = '${sheetNameType}'.`);

  return sheetNames;
}

function getToday(options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) {
  const date = new Date();
  let today;

  try {
    const dtf = new Intl.DateTimeFormat(locale, options);
    today = dtf.format(date);
  } catch (error) {
    // Logger.log(`Error formatting date: ${error.message}`);
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
  const sheet = new Sheet(sheetName);

  // Check if the sheet exists before trying to activate it.
  if (sheet) {
    sheet.activate();
  } else {
    // Logger.log('Sheet not found: ' + sheetName);
  }
}

function goToSheetLastRow(sheetName) {
  const sheet = new Sheet(sheetName);
  sheet.setActiveRange(sheet.getRange(sheet.getLastRow(), 1));
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

function goToSheetHMRC_B() {
  goToSheet(HMRC_B.SHEET_NAME)
}

function goToSheetHMRC_S() {
  goToSheet(HMRC_S.SHEET.NAME)
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

function goToSheetPeople() {
  goToSheet('People')
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

function isAccountSheet(sheet) {
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
    // Logger.log(cell);

    newCell = cell.replace(/\n/g, " ");
    // Logger.log(newCell);

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
    // Logger.log("Cell contains a valid date.");
    return true;
  } else {
    // Logger.log("Cell does NOT contain a date.");
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

function logWithTimeInterval(message) {
  const time = new Date().getTime();
  const timeDiffMs = time - previousTime;
  // Logger.log(`After ${timeDiffMs} milleseconds - ${message}`);
  previousTime = time;
}

function mergeTransactions() {
  const transactions = new Transactions();
  const transactionsBuilder = new TransactionsBuilder();
  const transactionFormulas = transactionsBuilder.getTransactionFormulas();

  transactions.updateBuilderFormulas(transactionFormulas);

  transactions.activate();
}

function monthlyUpdate() {
  const ourFinances = new OurFinances();
  ourFinances.bankAccounts.showMonthly();
}

// onDateChange is not a Google trigger; it must be created under Triggers (time based)!!!
function onDateChange() {
  sendDailyEmail();
  dailySorts();
}

function onEdit(event) {
  Logger.log('onEdit started');
  // Logger.log(JSON.stringify(event));
  const trigger = new Trigger(event);
  const sheet = trigger.getSheet();
  const sheetName = trigger.getSheetName();

  if (sheetName == HMRC_S.SHEET.NAME) {
    // Logger.log(`sheetName: ${sheetName}`);
    const hmrcS = new HMRC_S();
    hmrcS.handleEdit(trigger);
  }

  const bankAccounts = new BankAccounts();
  bankAccounts.updateLastUpdatedBySheet(sheet);

  Logger.log('onEdit finished');
}

function onOpen() {
  const spreadsheet = activeSpreadsheet;

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

function sendDailyEmail() {
  const ourFinances = new OurFinances();
  const fixedAmountMismatches = ourFinances.getFixedAmountMismatches();
  const upcomingDebits = ourFinances.getUpcomingDebits();

  const subject = `Our finances daily email: ${getToday()}`;

  // Initialize the email body
  let emailBody = ``;

  if (fixedAmountMismatches.length > 0) {
    emailBody += `Fixed amount mismatches\n`;
    // Concatenate the fixedAmountMismatches into the email body
    emailBody += fixedAmountMismatches.join("\n");
    emailBody += `\n\n`;
  }

  if (upcomingDebits.length) {
    emailBody += `Upcoming debits\n`;
    // Concatenate the debits into the email body
    emailBody += upcomingDebits.join("\n");
    emailBody += `\n\n`;
  }

  // Logger.log(`Email Body: ${emailBody}`);

  // Append the spreadsheet URL
  emailBody += `\n\nSent from (sendDailyEmail): ${ourFinances.spreadsheet.getUrl()}\n`;

  // Send the email
  sendMeEmail(subject, emailBody);
};

function sendEmail(recipient, subject, body, options) {
  return GmailApp.sendEmail(recipient, subject, body, options);
}

function sendMeEmail(subject, emailBody, options) {
  const body = `${subject}\n\n${emailBody}`;
  return sendEmail(getMyEmailAddress(), subject, body, options);
}

function setLastUpdatedOnAccountBalanceChange(sheet) {
  if (isAccountSheet(sheet)) {
    const bankAccounts = new BankAccounts();

    const key = sheet.getSheetName().slice(1);
    // logWithTimeInterval(`key: ${key}`);

    bankAccounts.updateLastUpdatedByKey(key);
  }
}

function setupDaysIterator(startDate) {
  const getNextResult = (iteratorDate) => {
    const date = cloneDate(iteratorDate);  // Default date in long format
    const day = getDtf().format(date);     // 19/01/1964
    const dayName = getDayName(date);      // Sunday
    const dayOfMonth = getDayOfMonth(date);  // 29
    const season = getSeasonName(date);  // Winter, Spring, Summer, Autumn

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

function sortGoogleSheets() {
  const ss = activeSpreadsheet;

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

function toValidFunctionName(str) {
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
    sheet = activeSpreadsheet.getActiveSheet();
  }

  sheet.trimSheet();
}

function trimGoogleSheets() {
  const sheets = activeSpreadsheet.getSheets();
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

  // Logger.log(`Value '${searchValue}' not found in column ${searchCol}`);
  return null;  // Return null if no match is found
}

// Main program starts here

const locale = 'en-GB';

logWithTimeInterval(`# ${getLineNumber()} Main program started`);

const activeSpreadsheet = new Spreadsheet();
logWithTimeInterval(`# ${getLineNumber()}`);

const gasSpreadsheetApp = SpreadsheetApp;

// logWithTimeInterval(getLineNumber());

logWithTimeInterval(`# ${getLineNumber()}`);

const accountSheetNames = getSheetNamesByType('account');
const dynamicFunctions = accountSheetNames.reduce((acc, sheetName) => {
  const funName = `dynamicAccount${sheetName}`;
  acc[funName] = () => goToSheetLastRow(sheetName);
  return acc;
}, {});

logWithTimeInterval(`# ${getLineNumber()}`);

// Logger.log('Assigning dynamic functions');

Object.assign(this, dynamicFunctions);

logWithTimeInterval(`# ${getLineNumber()}`);

