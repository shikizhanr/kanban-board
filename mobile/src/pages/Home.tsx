import React, { useState, useEffect } from 'react';
import { 
  IonPage, 
  IonHeader, 
  IonToolbar, 
  IonTitle, 
  IonContent, 
  IonList, 
  IonItem, 
  IonLabel, 
  IonLoading, 
  IonText, 
  IonButton,
  IonAlert,
  IonRefresher,
  IonRefresherContent,
  IonToggle,
  IonIcon,
  IonToast
} from '@ionic/react';
import { moon, checkmark } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { getPosts, Post } from '../services/api'; // Import API service and Post interface
import ItemCard from '../components/ItemCard'; // Import ItemCard

const Home: React.FC = () => {
  const history = useHistory();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    // Check initial theme preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDarkMode(prefersDark);
    toggleDarkTheme(prefersDark);

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getPosts();
        setPosts(data);
      } catch (err) {
        setError('Failed to fetch posts. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const doRefresh = async (event: CustomEvent) => {
    try {
      setError(null);
      const data = await getPosts();
      setPosts(data);
      setShowToast(true); // Show toast on successful refresh
    } catch (err) {
      setError('Failed to refresh posts. Please try again later.');
      console.error(err);
    } finally {
      event.detail.complete();
    }
  };

  const toggleDarkTheme = (shouldAdd: boolean) => {
    document.body.classList.toggle('dark', shouldAdd);
    setIsDarkMode(shouldAdd);
  };

  const handleThemeToggle = (event: CustomEvent) => {
    toggleDarkTheme(event.detail.checked);
  };

  const goToAboutPage = () => {
    history.push('/about');
  };

  const goToDetailPage = (id: number) => {
    history.push(`/detail/${id}`);
  };

  if (loading) {
    return <IonLoading isOpen={loading} message="Loading articles..." />;
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Home - Articles</IonTitle>
          <IonButtons slot="end">
            <IonIcon icon={moon} style={{ marginRight: '5px' }} />
            <IonToggle checked={isDarkMode} onIonChange={handleThemeToggle} />
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonHeader collapse="condense">
          <IonToolbar>
            <IonTitle size="large">Home - Articles</IonTitle>
          </IonToolbar>
        </IonHeader>

        <IonRefresher slot="fixed" onIonRefresh={doRefresh}>
          <IonRefresherContent></IonRefresherContent>
        </IonRefresher>
        
        <IonButton expand="full" onClick={goToAboutPage} style={{ margin: '10px 0' }}>
          Go to About Page
        </IonButton>

        {error && (
          <IonAlert
            isOpen={!!error}
            onDidDismiss={() => setError(null)}
            header={'Error'}
            message={error}
            buttons={['OK']}
          />
        )}

        {!loading && !error && posts.length === 0 && (
          <IonText style={{ textAlign: 'center', display: 'block', marginTop: '20px' }}>
            <p>No articles found.</p>
          </IonText>
        )}

        <IonList>
          {posts.map(post => (
            // Using ItemCard component as requested
            <ItemCard 
              key={post.id}
              title={post.title}
              content={post.body.substring(0, 100) + '...'}
              onClick={() => goToDetailPage(post.id)}
            />
            // Or using IonItem directly if ItemCard is not preferred for lists
            // <IonItem key={post.id} button onClick={() => goToDetailPage(post.id)} detail>
            //   <IonLabel>
            //     <h2>{post.title}</h2>
            //     <p>{post.body.substring(0, 100)}...</p>
            //   </IonLabel>
            // </IonItem>
          ))}
        </IonList>
        <IonToast
          isOpen={showToast}
          onDidDismiss={() => setShowToast(false)}
          message="Articles refreshed successfully!"
          duration={2000}
          position="top"
          icon={checkmark}
          color="success"
        />
      </IonContent>
    </IonPage>
  );
};

export default Home;
