/**
 * Help Panel Component for Angular (URS IR-3)
 *
 * This component implements the contextual help and suggestions requirement
 * from URS v2.0. It provides inline guidance on:
 * - CSV/Excel file format requirements
 * - Example commands
 * - Field mappings
 * - Common errors and solutions
 */
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';

@Component({
  selector: 'app-help-panel',
  standalone: true,
  imports: [
    CommonModule,
    MatExpansionModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatChipsModule,
  ],
  template: `
    <div class="help-panel">
      <div class="help-header">
        <mat-icon>help_outline</mat-icon>
        <h3>Quick Help & Tips</h3>
      </div>

      <mat-accordion class="help-accordion">
        <!-- CSV Upload Guide -->
        <mat-expansion-panel>
          <mat-expansion-panel-header>
            <mat-panel-title>
              <mat-icon>file_upload</mat-icon>
              CSV/Excel File Format
            </mat-panel-title>
          </mat-expansion-panel-header>

          <div class="help-content">
            <h4>Required Columns</h4>
            <mat-chip-set>
              <mat-chip *ngFor="let col of requiredColumns">{{ col }}</mat-chip>
            </mat-chip-set>

            <h4>Optional Columns</h4>
            <mat-chip-set>
              <mat-chip *ngFor="let col of optionalColumns" class="optional-chip">{{ col }}</mat-chip>
            </mat-chip-set>

            <h4>Example Format</h4>
            <div class="code-block">
              <code>
FirstName,LastName,DOB,Gender,Phone,Email<br>
John,Doe,1985-03-15,M,555-0100,john&#64;example.com<br>
Jane,Smith,1990-07-22,F,555-0101,jane&#64;example.com
              </code>
            </div>

            <div class="tip-box">
              <mat-icon>lightbulb</mat-icon>
              <p><strong>Tip:</strong> You can also upload Excel (.xlsx, .xls) and PDF files!</p>
            </div>
          </div>
        </mat-expansion-panel>

        <!-- Example Commands -->
        <mat-expansion-panel>
          <mat-expansion-panel-header>
            <mat-panel-title>
              <mat-icon>chat_bubble</mat-icon>
              Example Commands
            </mat-panel-title>
          </mat-expansion-panel-header>

          <div class="help-content">
            <div class="command-example" *ngFor="let example of commandExamples">
              <div class="command-header">
                <mat-icon>arrow_forward</mat-icon>
                <strong>{{ example.title }}</strong>
              </div>
              <div class="command-text">"{{ example.command }}"</div>
            </div>
          </div>
        </mat-expansion-panel>

        <!-- Field Mappings -->
        <mat-expansion-panel>
          <mat-expansion-panel-header>
            <mat-panel-title>
              <mat-icon>swap_horiz</mat-icon>
              CSV Field Mappings
            </mat-panel-title>
          </mat-expansion-panel-header>

          <div class="help-content">
            <p>The system automatically maps common column name variations:</p>

            <div class="mapping-list">
              <div class="mapping-item" *ngFor="let mapping of fieldMappings">
                <div class="mapping-from">
                  <mat-chip-set>
                    <mat-chip *ngFor="let variant of mapping.variants">{{ variant }}</mat-chip>
                  </mat-chip-set>
                </div>
                <mat-icon class="mapping-arrow">arrow_forward</mat-icon>
                <div class="mapping-to">
                  <strong>{{ mapping.field }}</strong>
                </div>
              </div>
            </div>
          </div>
        </mat-expansion-panel>

        <!-- Common Issues -->
        <mat-expansion-panel>
          <mat-expansion-panel-header>
            <mat-panel-title>
              <mat-icon>error_outline</mat-icon>
              Common Issues & Solutions
            </mat-panel-title>
          </mat-expansion-panel-header>

          <div class="help-content">
            <div class="issue-item" *ngFor="let issue of commonIssues">
              <div class="issue-problem">
                <mat-icon color="warn">warning</mat-icon>
                <strong>{{ issue.problem }}</strong>
              </div>
              <div class="issue-solution">
                <mat-icon color="primary">check_circle</mat-icon>
                <span>{{ issue.solution }}</span>
              </div>
            </div>
          </div>
        </mat-expansion-panel>

        <!-- Mirth Status -->
        <mat-expansion-panel *ngIf="showHealthStatus">
          <mat-expansion-panel-header>
            <mat-panel-title>
              <mat-icon>monitor_heart</mat-icon>
              System Status
            </mat-panel-title>
          </mat-expansion-panel-header>

          <div class="help-content">
            <div class="status-info">
              <mat-icon>info</mat-icon>
              <p>Real-time connectivity status indicators show whether Mirth Connect and OpenEMR are available.</p>
            </div>

            <div class="status-legend">
              <div class="legend-item">
                <span class="status-indicator healthy"></span>
                <span>Healthy - All systems operational</span>
              </div>
              <div class="legend-item">
                <span class="status-indicator degraded"></span>
                <span>Degraded - Partial functionality</span>
              </div>
              <div class="legend-item">
                <span class="status-indicator unhealthy"></span>
                <span>Unhealthy - System unavailable</span>
              </div>
            </div>
          </div>
        </mat-expansion-panel>
      </mat-accordion>
    </div>
  `,
  styles: [`
    .help-panel {
      background: white;
      border-radius: 8px;
      padding: 1rem;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .help-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
      color: #667eea;

      mat-icon {
        font-size: 28px;
        height: 28px;
        width: 28px;
      }

      h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
      }
    }

    .help-accordion {
      .mat-expansion-panel {
        margin-bottom: 0.5rem;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;

        &:not(.mat-expanded) {
          &:hover {
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
          }
        }
      }

      mat-panel-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;

        mat-icon {
          color: #667eea;
        }
      }
    }

    .help-content {
      padding: 1rem 0;

      h4 {
        margin: 0 0 0.5rem;
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      mat-chip-set {
        margin-bottom: 1rem;
      }

      .optional-chip {
        opacity: 0.7;
      }

      .code-block {
        background: #f5f7fa;
        border: 1px solid #e1e8ed;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        overflow-x: auto;

        code {
          color: #333;
          line-height: 1.6;
        }
      }

      .tip-box {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 4px;
        margin-top: 1rem;

        mat-icon {
          color: #2196f3;
          font-size: 24px;
          height: 24px;
          width: 24px;
        }

        p {
          margin: 0;
          color: #1565c0;
        }
      }
    }

    .command-example {
      margin-bottom: 1rem;
      padding: 0.75rem;
      background: #f8f9fa;
      border-radius: 4px;

      .command-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        color: #333;

        mat-icon {
          font-size: 18px;
          height: 18px;
          width: 18px;
          color: #667eea;
        }
      }

      .command-text {
        font-style: italic;
        color: #657786;
        padding-left: 26px;
      }
    }

    .mapping-list {
      .mapping-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: #f8f9fa;
        border-radius: 4px;

        .mapping-from {
          flex: 1;
        }

        .mapping-arrow {
          color: #8899a6;
        }

        .mapping-to {
          flex: 1;
          text-align: right;
          color: #667eea;
        }
      }
    }

    .issue-item {
      margin-bottom: 1.5rem;

      .issue-problem {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        color: #d32f2f;

        mat-icon {
          font-size: 20px;
          height: 20px;
          width: 20px;
        }
      }

      .issue-solution {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-left: 28px;
        color: #333;

        mat-icon {
          font-size: 18px;
          height: 18px;
          width: 18px;
        }
      }
    }

    .status-info {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      margin-bottom: 1rem;
      padding: 1rem;
      background: #f5f7fa;
      border-radius: 4px;

      mat-icon {
        color: #667eea;
      }

      p {
        margin: 0;
        color: #333;
      }
    }

    .status-legend {
      .legend-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;

          &.healthy {
            background: #4caf50;
          }

          &.degraded {
            background: #ff9800;
          }

          &.unhealthy {
            background: #f44336;
          }
        }

        span {
          color: #333;
          font-size: 0.9rem;
        }
      }
    }
  `]
})
export class HelpPanelComponent {
  @Input() showHealthStatus = true;

  requiredColumns = ['FirstName', 'LastName', 'DOB', 'Gender'];
  optionalColumns = ['Phone', 'Email', 'Address', 'City', 'State', 'Zip', 'SSN', 'MRN'];

  commandExamples = [
    {
      title: 'Upload a CSV file',
      command: 'Upload the attached CSV file and create patients'
    },
    {
      title: 'Create a single patient',
      command: 'Create a patient named John Doe born on March 15, 1985'
    },
    {
      title: 'Create multiple patients',
      command: 'Create 5 test patients'
    },
  ];

  fieldMappings = [
    {
      field: 'First Name',
      variants: ['FirstName', 'first_name', 'First', 'Given Name']
    },
    {
      field: 'Last Name',
      variants: ['LastName', 'last_name', 'Last', 'Surname', 'Family Name']
    },
    {
      field: 'Date of Birth',
      variants: ['DOB', 'DateOfBirth', 'Birth Date', 'Birthdate']
    },
    {
      field: 'Gender',
      variants: ['Gender', 'Sex', 'M/F']
    },
  ];

  commonIssues = [
    {
      problem: 'File upload fails',
      solution: 'Ensure your file is in CSV, Excel (.xlsx, .xls), or PDF format and is properly formatted'
    },
    {
      problem: 'Missing required fields',
      solution: 'Verify your file contains at least FirstName, LastName, DOB, and Gender columns'
    },
    {
      problem: 'Date format errors',
      solution: 'Use ISO format (YYYY-MM-DD) or common formats like MM/DD/YYYY for dates'
    },
    {
      problem: 'Duplicate patient records',
      solution: 'Check MRN (Medical Record Number) uniqueness before uploading'
    },
  ];
}
