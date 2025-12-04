/**
 * Confirmation Dialog Component for Angular (URS FR-3)
 *
 * This component implements the confirmation dialog requirement from URS v2.0.
 * It shows a preview of bulk operations before execution, allowing users to
 * review and confirm or cancel the operation.
 */
import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { MatChipsModule } from '@angular/material/chips';

export interface PatientPreview {
  name: string;
  mrn?: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface ConfirmationDialogData {
  preview_id: string;
  operation_type: string;
  total_records: number;
  preview_records: PatientPreview[];
  validation_warnings: string[];
  estimated_time_seconds?: number;
  message: string;
}

@Component({
  selector: 'app-confirmation-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatListModule,
    MatChipsModule,
  ],
  template: `
    <div class="confirmation-dialog">
      <!-- Header -->
      <div class="dialog-header">
        <h2 mat-dialog-title>
          <mat-icon>preview</mat-icon>
          Confirm Operation
        </h2>
      </div>

      <!-- Content -->
      <mat-dialog-content class="dialog-content">
        <!-- Message -->
        <div class="message-section">
          <p class="main-message">{{ data.message }}</p>
        </div>

        <!-- Summary Stats -->
        <div class="stats-section">
          <div class="stat-card">
            <mat-icon>person</mat-icon>
            <div class="stat-info">
              <span class="stat-label">Total Records</span>
              <span class="stat-value">{{ data.total_records }}</span>
            </div>
          </div>

          <div class="stat-card" *ngIf="data.estimated_time_seconds">
            <mat-icon>schedule</mat-icon>
            <div class="stat-info">
              <span class="stat-label">Estimated Time</span>
              <span class="stat-value">{{ formatTime(data.estimated_time_seconds) }}</span>
            </div>
          </div>
        </div>

        <!-- Validation Warnings -->
        <div class="warnings-section" *ngIf="data.validation_warnings && data.validation_warnings.length > 0">
          <h3>
            <mat-icon>warning</mat-icon>
            Warnings
          </h3>
          <mat-chip-set>
            <mat-chip *ngFor="let warning of data.validation_warnings" color="warn">
              {{ warning }}
            </mat-chip>
          </mat-chip-set>
        </div>

        <!-- Preview Records -->
        <div class="preview-section">
          <h3>
            <mat-icon>visibility</mat-icon>
            Preview (First {{ data.preview_records.length }} of {{ data.total_records }})
          </h3>

          <mat-list class="patient-list">
            <mat-list-item *ngFor="let patient of data.preview_records; let i = index">
              <div class="patient-card">
                <div class="patient-header">
                  <span class="patient-number">{{ i + 1 }}</span>
                  <span class="patient-name">{{ patient.name }}</span>
                  <mat-chip *ngIf="patient.mrn" class="mrn-chip">
                    MRN: {{ patient.mrn }}
                  </mat-chip>
                </div>

                <div class="patient-details">
                  <div class="detail-item" *ngIf="patient.date_of_birth">
                    <mat-icon>cake</mat-icon>
                    <span>DOB: {{ patient.date_of_birth }}</span>
                  </div>
                  <div class="detail-item" *ngIf="patient.gender">
                    <mat-icon>wc</mat-icon>
                    <span>{{ patient.gender }}</span>
                  </div>
                  <div class="detail-item" *ngIf="patient.phone">
                    <mat-icon>phone</mat-icon>
                    <span>{{ patient.phone }}</span>
                  </div>
                  <div class="detail-item" *ngIf="patient.email">
                    <mat-icon>email</mat-icon>
                    <span>{{ patient.email }}</span>
                  </div>
                </div>
              </div>
            </mat-list-item>
          </mat-list>

          <p class="more-records" *ngIf="data.total_records > data.preview_records.length">
            ...and {{ data.total_records - data.preview_records.length }} more record(s)
          </p>
        </div>
      </mat-dialog-content>

      <!-- Actions -->
      <mat-dialog-actions class="dialog-actions">
        <button mat-stroked-button (click)="onCancel()" color="warn">
          <mat-icon>cancel</mat-icon>
          Cancel
        </button>
        <button mat-raised-button (click)="onConfirm()" color="primary">
          <mat-icon>check_circle</mat-icon>
          Confirm and Proceed
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .confirmation-dialog {
      width: 600px;
      max-width: 90vw;
    }

    .dialog-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 1rem;
      margin: -24px -24px 0;

      h2 {
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;

        mat-icon {
          font-size: 28px;
          height: 28px;
          width: 28px;
        }
      }
    }

    .dialog-content {
      padding: 1.5rem 0 !important;
      max-height: 70vh;
      overflow-y: auto;
    }

    .message-section {
      margin-bottom: 1.5rem;

      .main-message {
        font-size: 1.1rem;
        color: #333;
        margin: 0;
      }
    }

    .stats-section {
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;

      .stat-card {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: #f5f7fa;
        border-radius: 8px;
        border: 1px solid #e1e8ed;

        mat-icon {
          color: #667eea;
          font-size: 32px;
          height: 32px;
          width: 32px;
        }

        .stat-info {
          display: flex;
          flex-direction: column;

          .stat-label {
            font-size: 0.75rem;
            color: #8899a6;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .stat-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
          }
        }
      }
    }

    .warnings-section {
      margin-bottom: 1.5rem;
      padding: 1rem;
      background: #fff3cd;
      border-left: 4px solid #ffc107;
      border-radius: 4px;

      h3 {
        margin: 0 0 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #856404;

        mat-icon {
          color: #ffc107;
        }
      }
    }

    .preview-section {
      h3 {
        margin: 0 0 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #333;
        font-size: 1rem;

        mat-icon {
          color: #667eea;
        }
      }

      .patient-list {
        padding: 0;

        mat-list-item {
          height: auto !important;
          padding: 0 !important;
          margin-bottom: 1rem;
        }
      }

      .patient-card {
        width: 100%;
        padding: 1rem;
        background: #f8f9fa;
        border: 1px solid #e1e8ed;
        border-radius: 8px;
        transition: all 0.2s ease;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          border-color: #667eea;
        }

        .patient-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.75rem;

          .patient-number {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            font-weight: 600;
            font-size: 0.875rem;
          }

          .patient-name {
            flex: 1;
            font-weight: 600;
            font-size: 1rem;
            color: #333;
          }

          .mrn-chip {
            font-size: 0.75rem;
          }
        }

        .patient-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 0.5rem;
          padding-left: 38px;

          .detail-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            color: #657786;

            mat-icon {
              font-size: 18px;
              height: 18px;
              width: 18px;
              color: #8899a6;
            }
          }
        }
      }

      .more-records {
        text-align: center;
        color: #8899a6;
        font-style: italic;
        margin-top: 1rem;
      }
    }

    .dialog-actions {
      padding: 1rem 0 0 !important;
      margin: 0 !important;
      border-top: 1px solid #e1e8ed;
      gap: 1rem;
      justify-content: flex-end;

      button {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        mat-icon {
          font-size: 20px;
          height: 20px;
          width: 20px;
        }
      }
    }
  `]
})
export class ConfirmationDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmationDialogData
  ) {}

  onConfirm(): void {
    this.dialogRef.close({ confirmed: true, preview_id: this.data.preview_id });
  }

  onCancel(): void {
    this.dialogRef.close({ confirmed: false });
  }

  formatTime(seconds: number): string {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }
}
