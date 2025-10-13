import React, { useEffect, useMemo, useState } from 'react';
import { Alert, View } from 'react-native';
import Pdf from 'react-native-pdf';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

import AnnotationToolbar from '@components/documents/AnnotationToolbar';
import LoadingOverlay from '@components/common/LoadingOverlay';
import { RootStackParamList } from '@navigation/RootNavigator';
import { useAppDispatch } from '@hooks/useAppDispatch';
import { useAppSelector } from '@hooks/useAppSelector';
import { downloadDocumentThunk, selectDocumentById } from '@store/slices/documentsSlice';
import { saveAnnotationThunk } from '@store/slices/annotationsSlice';

import styles from './styles/DocumentViewerScreen.styles';

export type DocumentViewerScreenProps = NativeStackScreenProps<RootStackParamList, 'DocumentViewer'>;

const DocumentViewerScreen: React.FC<DocumentViewerScreenProps> = ({ route }) => {
  const { dealId, documentId } = route.params;
  const dispatch = useAppDispatch();
  const document = useAppSelector((state) => selectDocumentById(state, documentId));
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    if (!document?.localPath) {
      dispatch(downloadDocumentThunk({ dealId, documentId }));
    }
  }, [dealId, document, documentId, dispatch]);

  const source = useMemo(() => {
    if (document?.localPath) {
      return { uri: document.localPath };
    }
    if (document?.remoteUrl) {
      return { uri: document.remoteUrl, cache: true };
    }
    return undefined;
  }, [document]);

  const handleAnnotationSave = async (annotation: string) => {
    if (!document) {
      return;
    }
    const result = await dispatch(
      saveAnnotationThunk({
        documentId,
        page: currentPage,
        annotation
      })
    );
    if (saveAnnotationThunk.rejected.match(result)) {
      Alert.alert('Annotation failed', result.error.message ?? 'Please try again.');
    }
  };

  if (!source) {
    return <LoadingOverlay message="Preparing document..." />;
  }

  return (
    <View style={styles.container}>
      <Pdf
        trustAllCerts={false}
        source={source}
        onPageChanged={setCurrentPage}
        style={styles.pdf}
        enablePaging
      />
      <AnnotationToolbar onSaveAnnotation={handleAnnotationSave} currentPage={currentPage} />
    </View>
  );
};

export default DocumentViewerScreen;
