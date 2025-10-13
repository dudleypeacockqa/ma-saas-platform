export type Annotation = {
  id: string;
  documentId: string;
  page: number;
  contents: string;
  createdAt: string;
  author: string;
  synced: boolean;
};

export type Document = {
  id: string;
  title: string;
  remoteUrl: string;
  localPath?: string;
  mimeType: string;
  sizeInBytes: number;
  lastUpdatedAt: string;
  annotations: Annotation[];
};
