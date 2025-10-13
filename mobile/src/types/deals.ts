export type DealStage =
  | 'sourcing'
  | 'evaluation'
  | 'due_diligence'
  | 'negotiation'
  | 'signed'
  | 'closed';

export type DealDocument = {
  id: string;
  title: string;
  remoteUrl: string;
  localPath?: string;
  lastUpdatedAt: string;
  sizeInBytes: number;
  annotatedBy?: string;
};

export type DealTimelineEvent = {
  id: string;
  occurredAt: string;
  summary: string;
  actor: string;
  type: 'comment' | 'update' | 'document' | 'milestone';
};

export type Deal = {
  id: string;
  name: string;
  stage: DealStage;
  stageLabel: string;
  value: number;
  formattedValue: string;
  ownerId: string;
  ownerName: string;
  lastActivityAt: string;
  lastActivityLabel: string;
  lastSyncedAt?: string;
  documents: DealDocument[];
  timeline: DealTimelineEvent[];
  hasOfflineChanges?: boolean;
};

export type DealListItem = Pick<Deal, 'id' | 'name' | 'stageLabel' | 'formattedValue' | 'ownerName' | 'lastActivityLabel' | 'hasOfflineChanges' | 'documents'>;
