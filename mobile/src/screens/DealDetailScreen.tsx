import React, { useEffect, useMemo } from 'react';
import { ScrollView, View } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

import DocumentListItem from '@components/documents/DocumentListItem';
import KeyValueRow from '@components/common/KeyValueRow';
import SectionHeader from '@components/common/SectionHeader';
import EmptyState from '@components/common/EmptyState';
import LoadingOverlay from '@components/common/LoadingOverlay';
import { RootStackParamList } from '@navigation/RootNavigator';
import { useAppDispatch } from '@hooks/useAppDispatch';
import { useAppSelector } from '@hooks/useAppSelector';
import { fetchDealByIdThunk, selectDealById } from '@store/slices/dealsSlice';

import styles from './styles/DealDetailScreen.styles';

export type DealDetailScreenProps = NativeStackScreenProps<RootStackParamList, 'DealDetail'>;

const DealDetailScreen: React.FC<DealDetailScreenProps> = ({ route, navigation }) => {
  const { dealId } = route.params;
  const dispatch = useAppDispatch();
  const deal = useAppSelector((state) => selectDealById(state, dealId));
  const isLoading = useAppSelector((state) => state.deals.status === 'loading');

  useEffect(() => {
    if (!deal) {
      dispatch(fetchDealByIdThunk({ dealId }));
    }
  }, [deal, dealId, dispatch]);

  const documents = useMemo(() => deal?.documents ?? [], [deal]);

  if (isLoading && !deal) {
    return <LoadingOverlay message="Loading deal..." />;
  }

  if (!deal) {
    return <EmptyState title="Deal unavailable" message="This deal could not be loaded." />;
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <SectionHeader title="Summary" />
        <KeyValueRow label="Stage" value={deal.stageLabel} />
        <KeyValueRow label="Value" value={deal.formattedValue} />
        <KeyValueRow label="Owner" value={deal.ownerName} />
        <KeyValueRow label="Last activity" value={deal.lastActivityLabel} />
      </View>

      <View style={styles.section}>
        <SectionHeader title="Documents" actionLabel="See all" onActionPress={() => navigation.navigate('DocumentViewer', { dealId, documentId: documents[0]?.id ?? '' })} />
        {documents.length ? (
          documents.map((document) => (
            <DocumentListItem
              key={document.id}
              document={document}
              onPress={() =>
                navigation.navigate('DocumentViewer', { dealId, documentId: document.id })
              }
            />
          ))
        ) : (
          <EmptyState title="No documents" message="Documents you have access to will appear here." compact />
        )}
      </View>
    </ScrollView>
  );
};

export default DealDetailScreen;
