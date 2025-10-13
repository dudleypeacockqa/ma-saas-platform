import React, { useCallback, useEffect } from 'react';
import { FlatList, RefreshControl, View } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

import DealCard from '@components/deals/DealCard';
import EmptyState from '@components/common/EmptyState';
import LoadingOverlay from '@components/common/LoadingOverlay';
import { RootStackParamList } from '@navigation/RootNavigator';
import { useAppDispatch } from '@hooks/useAppDispatch';
import { useAppSelector } from '@hooks/useAppSelector';
import { fetchDealsThunk, selectAllDeals } from '@store/slices/dealsSlice';

import styles from './styles/DealListScreen.styles';

export type DealListScreenProps = NativeStackScreenProps<RootStackParamList, 'DealList'>;

const DealListScreen: React.FC<DealListScreenProps> = ({ navigation }) => {
  const dispatch = useAppDispatch();
  const deals = useAppSelector(selectAllDeals);
  const isLoading = useAppSelector((state) => state.deals.status === 'loading');
  const lastSyncedAt = useAppSelector((state) => state.deals.lastSyncedAt);
  const isOffline = useAppSelector((state) => state.offline.isOffline);

  useEffect(() => {
    dispatch(fetchDealsThunk({ forceRefresh: false }));
  }, [dispatch]);

  const handleRefresh = useCallback(() => {
    dispatch(fetchDealsThunk({ forceRefresh: true }));
  }, [dispatch]);

  if (isLoading && !deals.length) {
    return <LoadingOverlay message="Loading deals..." />;
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={deals}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <DealCard
            deal={item}
            lastSyncedAt={lastSyncedAt}
            isOffline={isOffline}
            onPress={() => navigation.navigate('DealDetail', { dealId: item.id })}
          />
        )}
        refreshControl={<RefreshControl refreshing={isLoading} onRefresh={handleRefresh} />}
        ListEmptyComponent={<EmptyState title="No deals" message="Pull to refresh your pipeline." />}
        contentContainerStyle={!deals.length ? styles.emptyContent : styles.listContent}
      />
    </View>
  );
};

export default DealListScreen;
