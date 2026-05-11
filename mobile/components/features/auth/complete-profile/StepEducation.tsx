import React, { memo } from 'react';
import { View, Pressable, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useTranslation } from 'react-i18next';
import { CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react-native';
import Animated, { FadeInDown, Layout } from 'react-native-reanimated';
import { useQuery } from '@tanstack/react-query';
import { metaService } from '../../../../src/services/meta.service';

const EDUCATION_LEVELS = [
  'freshman_sophomore', 'junior_senior', 'graduated', 'working'
];

interface UserSpecialization {
  specialization_id: string
  level: string
  skill_ids: string[]
}

interface StepEducationProps {
  specializations: UserSpecialization[]
  setSpecializations: (v: UserSpecialization[]) => void
}

const SelectionItem = memo(({ 
  label, 
  selected, 
  onToggle,
  onToggleExpand,
  level,
  onSelectLevel,
  isExpanded
}: { 
  label: string, 
  selected: boolean, 
  onToggle: () => void,
  onToggleExpand: () => void,
  level?: string,
  onSelectLevel?: (l: string) => void,
  isExpanded?: boolean
}) => {
  const { t } = useTranslation();
  return (
    <View style={[styles.itemContainer, selected && styles.itemContainerSelected]}>
      <View style={styles.itemHeader}>
        <Pressable 
          onPress={onToggleExpand}
          style={styles.headerTextContainer}
        >
          <Text style={[
            styles.itemText,
            selected && styles.itemTextSelected
          ]}>
            {label}
          </Text>
          {selected && (
            <View style={styles.selectedBadge}>
              <Text style={styles.levelBadgeText}>
                {level ? t(`auth.profile.education.levels.${level}`) : t('common.select_level')}
              </Text>
            </View>
          )}
        </Pressable>

        <Pressable 
          onPress={onToggle}
          style={styles.rightIcons}
          hitSlop={15}
        >
          {selected ? (
            <View style={styles.checkContainer}>
              <CheckCircle2 size={24} color="#059669" fill="rgba(16,185,129,0.1)" />
            </View>
          ) : (
            <View style={styles.emptyCircle} />
          )}
        </Pressable>
      </View>

      {selected && isExpanded && (
        <Animated.View entering={FadeInDown} style={styles.levelContainer}>
          {EDUCATION_LEVELS.map((l) => (
            <Pressable 
              key={l} 
              onPress={() => onSelectLevel?.(l)}
              style={[styles.levelItem, level === l && styles.levelItemSelected]}
            >
              <Text style={[styles.levelText, level === l && styles.levelTextSelected]}>
                {t(`auth.profile.education.levels.${l}`)}
              </Text>
              {level === l && <CheckCircle2 size={16} color="#059669" />}
            </Pressable>
          ))}
        </Animated.View>
      )}
    </View>
  );
});

export function StepEducation({
  specializations, setSpecializations
}: StepEducationProps) {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language === 'vi' ? 'vi' : 'en';

  const { data: remoteSpecs, isLoading } = useQuery({
    queryKey: ['specializations'],
    queryFn: metaService.getSpecializations
  });

  const [expandedIndex, setExpandedIndex] = React.useState<number | null>(
    specializations.length > 0 ? 0 : null
  );

  const toggleSpecialization = (id: string) => {
    setSpecializations(prev => {
      const exists = prev.find(s => s.specialization_id === id);
      if (exists) {
        setExpandedIndex(null);
        return prev.filter(s => s.specialization_id !== id);
      } else {
        const newList = [...prev, { specialization_id: id, level: '', skill_ids: [] }];
        setExpandedIndex(newList.length - 1);
        return newList;
      }
    });
  };

  const updateLevel = (id: string, level: string) => {
    setSpecializations(prev => prev.map(s => 
      s.specialization_id === id ? { ...s, level } : s
    ));
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator color="#10b981" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>{t('auth.profile.education.specialization')}</Text>
      <Animated.View layout={Layout.springify()} style={styles.listContainer}>
        {remoteSpecs?.map((spec, index) => {
          const displayName = currentLang === 'vi' ? spec.name_vi : spec.name_en;
          const specData = specializations.find(item => item.specialization_id === spec.id);
          const isSelected = !!specData;
          const listIndex = specializations.findIndex(item => item.specialization_id === spec.id);
          
          return (
            <SelectionItem 
              key={spec.id}
              label={displayName}
              selected={isSelected}
              isExpanded={expandedIndex === listIndex && isSelected}
              level={specData?.level}
              onToggle={() => toggleSpecialization(spec.id)}
              onToggleExpand={() => {
                if (isSelected) {
                  setExpandedIndex(expandedIndex === listIndex ? null : listIndex);
                } else {
                  toggleSpecialization(spec.id);
                }
              }}
              onSelectLevel={(l) => updateLevel(spec.id, l)}
            />
          );
        })}
      </Animated.View>

      {specializations.length > 0 && (
        <Text style={styles.hintText}>
          * Bạn có thể chọn nhiều ngành và đặt trình độ riêng cho mỗi ngành.
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingVertical: 10,
  },
  loadingContainer: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center'
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#71717a',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 16,
    marginLeft: 4,
  },
  listContainer: {
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: 24,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.4)',
  },
  itemContainer: {
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.2)',
  },
  itemContainerSelected: {
    backgroundColor: 'rgba(16,185,129,0.12)',
  },
  itemHeader: {
    paddingHorizontal: 20,
    paddingVertical: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerTextContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  itemText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#27272a',
  },
  itemTextSelected: {
    color: '#059669',
    fontWeight: '800',
  },
  rightIcons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  checkContainer: {
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: 'rgba(113,113,122,0.4)',
  },
  selectedBadge: {
    backgroundColor: 'rgba(16,185,129,0.15)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(16,185,129,0.3)',
  },
  levelBadgeText: {
    fontSize: 12,
    color: '#059669',
    fontWeight: '800',
  },
  levelContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
    gap: 10,
  },
  levelItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.5)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  levelItemSelected: {
    backgroundColor: 'rgba(16,185,129,0.2)',
    borderColor: 'rgba(16,185,129,0.4)',
  },
  levelText: {
    fontSize: 15,
    color: '#3f3f46',
    fontWeight: '700',
  },
  levelTextSelected: {
    color: '#059669',
    fontWeight: '900',
  },
  hintText: {
    marginTop: 16,
    fontSize: 13,
    color: '#52525b',
    fontWeight: '500',
    fontStyle: 'italic',
    paddingHorizontal: 8,
    lineHeight: 18,
  }
});
