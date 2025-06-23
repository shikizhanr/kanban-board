import React, { useState, useEffect } from 'react';
import { 
  IonPage, 
  IonHeader, 
  IonToolbar, 
  IonTitle, 
  IonContent, 
  IonButtons, 
  IonBackButton, 
  IonLoading, 
  IonText,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonAlert
} from '@ionic/react';
import { useParams } from 'react-router-dom';
import { getPostById, Post } from '../services/api'; // Import API service and Post interface

interface DetailPageParams {
  id: string; // id from URL is a string
}

const Detail: React.FC = () => {
  const { id } = useParams<DetailPageParams>();
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        setLoading(true);
        setError(null);
        const postId = parseInt(id, 10); // Convert id to number
        if (isNaN(postId)) {
          setError('Invalid post ID.');
          setLoading(false);
          return;
        }
        const data = await getPostById(postId);
        setPost(data);
      } catch (err) {
        setError('Failed to fetch post details. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchPost();
    }
  }, [id]);

  if (loading) {
    return <IonLoading isOpen={loading} message="Loading post details..." />;
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/home" />
          </IonButtons>
          <IonTitle>{post ? post.title : 'Detail'}</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonHeader collapse="condense">
          <IonToolbar>
            <IonTitle size="large">{post ? post.title : 'Detail'}</IonTitle>
          </IonToolbar>
        </IonHeader>

        {error && (
          <IonAlert
            isOpen={!!error}
            onDidDismiss={() => setError(null)}
            header={'Error'}
            message={error}
            buttons={['OK']}
          />
        )}

        {!loading && !error && !post && (
          <IonText style={{ textAlign: 'center', display: 'block', marginTop: '20px' }}>
            <p>Post not found.</p>
          </IonText>
        )}

        {post && (
          <IonCard>
            <IonCardHeader>
              <IonCardTitle>{post.title}</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <p>{post.body}</p>
            </IonCardContent>
          </IonCard>
        )}
      </IonContent>
    </IonPage>
  );
};

export default Detail;
